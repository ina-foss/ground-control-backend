"""APIRouter exposing user and role administration endpoints."""

import logging
import math
from typing import Generator, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlmodel import Session

from ina_ground_control.ina_user_admin.config import UserAdminSettings
from ina_ground_control.ina_user_admin.middleware.auth_dependencies import (
    AuthorizationResult,
    CheckPermissionsFromDB,
)
from ina_ground_control.ina_user_admin.repository import UserRepository
from ina_ground_control.ina_user_admin.schemas import (
    AssignRolesByNameRequest,
    AssignRolesRequest,
    BulkCreateUsersRequest,
    CreateRoleRequest,
    CreateUserRequest,
    PaginatedUsersResponse,
    RoleResponse,
    UpdateRoleRequest,
    UserWithRolesResponse,
)

logger = logging.getLogger(__name__)


def get_db(request: Request) -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session from the app's engine.

    Reads the SQLAlchemy engine from ``request.app.state.user_admin_engine``.

    Args:
        request: The current FastAPI request.

    Yields:
        An active ``Session`` instance that is closed after the request completes.
    """
    with Session(request.app.state.user_admin_engine) as session:
        yield session


def get_settings(request: Request) -> UserAdminSettings:
    """FastAPI dependency that returns the ``UserAdminSettings`` from app state.

    Args:
        request: The current FastAPI request.

    Returns:
        The ``UserAdminSettings`` instance stored in ``app.state``.
    """
    return request.app.state.user_admin_settings


async def require_admin(request: Request) -> AuthorizationResult:
    """FastAPI dependency that enforces the admin permission for the current request.

    The required admin permission is read from ``request.app.state.user_admin_settings``
    so that it can vary between consumer projects without code changes.

    Args:
        request: The current FastAPI request.

    Returns:
        An ``AuthorizationResult`` if the user holds the admin permission.

    Raises:
        HTTPException: 401 if the user is not authenticated.
        HTTPException: 403 if the user does not have the admin permission.
    """
    settings: UserAdminSettings = request.app.state.user_admin_settings
    checker = CheckPermissionsFromDB([settings.admin_permission])
    return await checker(request)


def _build_user_response(user, repo: UserRepository) -> UserWithRolesResponse:
    """Build a ``UserWithRolesResponse`` from a ``User`` ORM object.

    Loads the user's roles via the repository and assembles the full response DTO.

    Args:
        user: A ``User`` SQLModel instance.
        repo: An active ``UserRepository`` used to fetch role data.

    Returns:
        A populated ``UserWithRolesResponse`` DTO.
    """
    roles = repo.get_user_roles(user.email)
    role_responses = [RoleResponse.model_validate(r) for r in roles]
    return UserWithRolesResponse(
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        roles=role_responses,
    )


def create_user_router() -> APIRouter:
    """Create and return the user/role administration ``APIRouter``.

    All endpoints except none require admin permission (checked via ``require_admin``
    dependency). The router does not embed settings or DB details at construction
    time — those are resolved per-request from ``app.state``.

    Returns:
        A configured ``APIRouter`` with all user and role CRUD endpoints.
    """
    router = APIRouter()

    # ------------------------------------------------------------------
    # User endpoints
    # ------------------------------------------------------------------

    @router.get("/users", response_model=PaginatedUsersResponse)
    async def list_users(
        page: int = Query(default=0, ge=0),
        page_size: int = Query(default=20, ge=1, le=100),
        sort_by: Literal[
            "email",
            "firstname",
            "lastname",
            "is_active",
            "created_at",
            "updated_at",
            "last_login_at",
        ] = "email",
        sort_order: Literal["asc", "desc"] = "asc",
        search: str | None = None,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> PaginatedUsersResponse:
        """Return a paginated list of all users with their roles.

        Args:
            page: Zero-based page index (default 0).
            page_size: Items per page, max 100 (default 20).
            sort_by: Field to sort by (``email``, ``firstname``, etc.).
            sort_order: ``"asc"`` or ``"desc"``.
            search: Optional search string filtered against email/name fields.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            A ``PaginatedUsersResponse`` containing the current page of users.
        """
        repo = UserRepository(db)
        users, total = repo.get_users_paginated(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        )
        total_pages = math.ceil(total / page_size) if page_size else 0
        items = [_build_user_response(u, repo) for u in users]
        return PaginatedUsersResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @router.get("/users/emails", response_model=list[str])
    async def list_user_emails(
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> list[str]:
        """Return a flat list of all user email addresses.

        Args:
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            A list of email strings.
        """
        repo = UserRepository(db)
        return repo.get_all_users_emails()

    @router.post(
        "/users",
        response_model=UserWithRolesResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_user(
        body: CreateUserRequest,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> UserWithRolesResponse:
        """Create a single user and optionally assign roles by ID.

        Args:
            body: The creation request containing email, name, and optional role IDs.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            The newly created user with their roles (HTTP 201).

        Raises:
            HTTPException: 409 if the email is already registered.
            HTTPException: 404 if any role ID does not exist.
        """
        repo = UserRepository(db)
        user = repo.create_user(
            email=str(body.email),
            firstname=body.firstname,
            lastname=body.lastname,
            role_ids=body.role_ids,
        )
        return _build_user_response(user, repo)

    @router.post(
        "/users/bulk",
        response_model=list[UserWithRolesResponse],
        status_code=status.HTTP_201_CREATED,
    )
    async def bulk_create_users(
        body: BulkCreateUsersRequest,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> list[UserWithRolesResponse]:
        """Create multiple users at once with shared role assignments.

        Args:
            body: List of email addresses and optional shared role IDs.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            List of created (or pre-existing) users with their roles (HTTP 201).
        """
        repo = UserRepository(db)
        users = repo.bulk_create_users(
            emails=[str(e) for e in body.emails],
            role_ids=body.role_ids,
        )
        return [_build_user_response(u, repo) for u in users]

    @router.delete("/users/{email}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_user(
        email: str,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> None:
        """Delete a user and all their role assignments.

        Args:
            email: The email address of the user to delete.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Raises:
            HTTPException: 404 if no user with the given email exists.
        """
        repo = UserRepository(db)
        deleted = repo.delete_user(email)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"User '{email}' not found.")

    @router.get("/users/{email}/roles", response_model=list[RoleResponse])
    async def get_user_roles(
        email: str,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> list[RoleResponse]:
        """Return all roles assigned to a specific user.

        Args:
            email: The user's email address.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            A list of ``RoleResponse`` objects.

        Raises:
            HTTPException: 404 if the user does not exist.
        """
        repo = UserRepository(db)
        user = repo.get_user(email)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{email}' not found.")
        roles = repo.get_user_roles(email)
        return [RoleResponse.model_validate(r) for r in roles]

    @router.post("/users/{email}/roles", response_model=UserWithRolesResponse)
    async def assign_roles(
        email: str,
        body: AssignRolesRequest,
        request: Request,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> UserWithRolesResponse:
        """Add roles to a user without removing existing assignments.

        Args:
            email: The user's email address.
            body: The role IDs to assign.
            request: The current FastAPI request (used to identify assigned_by).
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            The updated user with all current roles.

        Raises:
            HTTPException: 404 if the user or any role does not exist.
        """
        repo = UserRepository(db)
        admin_user = request.scope.get("user")
        assigned_by = getattr(admin_user, "email", None)
        user = repo.assign_roles(
            email=email, role_ids=body.role_ids, assigned_by=assigned_by
        )
        return _build_user_response(user, repo)

    @router.put("/users/{email}/roles", response_model=UserWithRolesResponse)
    async def replace_roles(
        email: str,
        body: AssignRolesRequest,
        request: Request,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> UserWithRolesResponse:
        """Replace all of a user's roles with the provided list (by ID).

        Args:
            email: The user's email address.
            body: The role IDs that should be the user's complete role set.
            request: The current FastAPI request (used to identify assigned_by).
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            The updated user with the new role set.

        Raises:
            HTTPException: 404 if the user or any role does not exist.
        """
        repo = UserRepository(db)
        admin_user = request.scope.get("user")
        assigned_by = getattr(admin_user, "email", None)
        user = repo.replace_roles(
            email=email, role_ids=body.role_ids, assigned_by=assigned_by
        )
        return _build_user_response(user, repo)

    @router.put("/users/{email}/roles/update", response_model=UserWithRolesResponse)
    async def replace_roles_by_name(
        email: str,
        body: AssignRolesByNameRequest,
        request: Request,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> UserWithRolesResponse:
        """Replace all of a user's roles using role names, auto-creating missing roles.

        Args:
            email: The user's email address.
            body: The role names that should be the user's complete role set.
            request: The current FastAPI request (used to identify assigned_by).
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            The updated user with the new role set.

        Raises:
            HTTPException: 404 if the user does not exist.
        """
        repo = UserRepository(db)
        admin_user = request.scope.get("user")
        assigned_by = getattr(admin_user, "email", None)
        user = repo.replace_roles_by_name(
            email=email,
            role_names=body.role_names,
            assigned_by=assigned_by,
            auto_create=True,
        )
        return _build_user_response(user, repo)

    @router.delete(
        "/users/{email}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT
    )
    async def remove_role(
        email: str,
        role_id: int,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> None:
        """Remove a single role assignment from a user.

        Args:
            email: The user's email address.
            role_id: The ID of the role to remove.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Raises:
            HTTPException: 404 if the assignment does not exist.
        """
        repo = UserRepository(db)
        removed = repo.remove_role(email=email, role_id=role_id)
        if not removed:
            raise HTTPException(
                status_code=404,
                detail=f"Role assignment not found for user '{email}' and role {role_id}.",
            )

    # ------------------------------------------------------------------
    # Role endpoints
    # ------------------------------------------------------------------

    @router.get("/roles", response_model=list[RoleResponse])
    async def list_roles(
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> list[RoleResponse]:
        """Return all roles in the system.

        Args:
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            A list of all ``RoleResponse`` objects, ordered by name.
        """
        repo = UserRepository(db)
        roles = repo.get_all_roles()
        return [RoleResponse.model_validate(r) for r in roles]

    @router.post(
        "/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED
    )
    async def create_role(
        body: CreateRoleRequest,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> RoleResponse:
        """Create a new role.

        Args:
            body: The role name and optional description.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            The newly created ``RoleResponse`` (HTTP 201).

        Raises:
            HTTPException: 409 if a role with the given name already exists.
        """
        repo = UserRepository(db)
        role = repo.create_role(name=body.name, description=body.description)
        return RoleResponse.model_validate(role)

    @router.get("/roles/{role_id}", response_model=RoleResponse)
    async def get_role(
        role_id: int,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> RoleResponse:
        """Retrieve a role by its ID.

        Args:
            role_id: The role's integer primary key.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            The matching ``RoleResponse``.

        Raises:
            HTTPException: 404 if the role does not exist.
        """
        repo = UserRepository(db)
        role = repo.get_role(role_id)
        if role is None:
            raise HTTPException(
                status_code=404, detail=f"Role with id {role_id} not found."
            )
        return RoleResponse.model_validate(role)

    @router.put("/roles/{role_id}", response_model=RoleResponse)
    async def update_role(
        role_id: int,
        body: UpdateRoleRequest,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> RoleResponse:
        """Update an existing role's name and/or description.

        Args:
            role_id: The role's integer primary key.
            body: Fields to update (all optional).
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Returns:
            The updated ``RoleResponse``.

        Raises:
            HTTPException: 404 if the role does not exist.
            HTTPException: 409 if the new name conflicts with an existing role.
        """
        repo = UserRepository(db)
        role = repo.update_role(
            role_id=role_id, name=body.name, description=body.description
        )
        if role is None:
            raise HTTPException(
                status_code=404, detail=f"Role with id {role_id} not found."
            )
        return RoleResponse.model_validate(role)

    @router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_role(
        role_id: int,
        _auth: AuthorizationResult = Depends(require_admin),
        db: Session = Depends(get_db),
    ) -> None:
        """Delete a role and remove all user-role assignments referencing it.

        Args:
            role_id: The role's integer primary key.
            _auth: Admin permission check (injected).
            db: Database session (injected).

        Raises:
            HTTPException: 404 if the role does not exist.
        """
        repo = UserRepository(db)
        deleted = repo.delete_role(role_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail=f"Role with id {role_id} not found."
            )

    return router
