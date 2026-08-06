"""Database access layer for users, roles, and their associations."""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select

from ina_ground_control.ina_user_admin.repository.base_repository import BaseRepository
from ina_ground_control.models.role import Role
from ina_ground_control.models.user_model import User
from ina_ground_control.models.user_role import UserRole

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository providing all database operations for users, roles, and their associations.

    Inherits database session access from ``BaseRepository``. All methods use the
    session provided at construction time and do not manage transaction boundaries
    except where explicitly stated (``commit`` / ``rollback``).
    """

    # ------------------------------------------------------------------
    # User queries
    # ------------------------------------------------------------------

    def get_user(self, email: str) -> User | None:
        """Retrieve a user by email address without loading roles.

        Args:
            email: The user's email address (primary key).

        Returns:
            The ``User`` instance if found, otherwise ``None``.
        """
        return self._db_session.get(User, email)

    def get_user_with_roles(self, email: str) -> User | None:
        """Retrieve a user by email address and eagerly load their role associations.

        Args:
            email: The user's email address.

        Returns:
            The ``User`` instance with ``user_roles`` populated, or ``None`` if not found.
        """
        user = self._db_session.get(User, email)
        if user is None:
            return None
        # Access the relationship to trigger loading
        _ = user.user_roles
        return user

    def get_all_users_emails(self) -> list[str]:
        """Return a flat list of all user email addresses in the database.

        Returns:
            A list of email strings, unsorted.
        """
        results = self._db_session.exec(select(User.email)).all()
        return list(results)

    def get_users_paginated(
        self,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
        search: str | None,
    ) -> tuple[list[User], int]:
        """Return a paginated, optionally filtered and sorted list of users.

        Args:
            page: Zero-based page index.
            page_size: Maximum number of users to return per page (capped at 100).
            sort_by: Column name to sort by (``"email"``, ``"firstname"``, ``"lastname"``).
                     Defaults to ``"email"`` for unrecognised values.
            sort_order: ``"asc"`` or ``"desc"`` (case-insensitive). Defaults to ascending.
            search: Optional search string matched against email, firstname, and lastname
                    using a case-insensitive ``LIKE`` pattern. ``None`` disables filtering.

        Returns:
            A 2-tuple of ``(users, total)`` where ``total`` is the count of matching
            users before pagination is applied.
        """
        page_size = min(page_size, 100)

        stmt = select(User)

        if search:
            escaped = (
                search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            )
            pattern = f"%{escaped}%"
            stmt = stmt.where(
                col(User.email).ilike(pattern)
                | col(User.firstname).ilike(pattern)
                | col(User.lastname).ilike(pattern)
            )

        # Determine sort column
        sort_column = {
            "email": User.email,
            "firstname": User.firstname,
            "lastname": User.lastname,
            "is_active": User.is_active,
            "created_at": User.created_at,
            "updated_at": User.updated_at,
            "last_login_at": User.last_login_at,
        }.get(sort_by, User.email)

        if sort_order.lower() == "desc":
            stmt = stmt.order_by(col(sort_column).desc())
        else:
            stmt = stmt.order_by(col(sort_column).asc())

        # Count total matching rows
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self._db_session.exec(count_stmt).one()

        # Apply SQL-level pagination
        paginated_stmt = stmt.offset(page * page_size).limit(page_size)
        users = list(self._db_session.exec(paginated_stmt).all())

        return users, total

    # ------------------------------------------------------------------
    # User mutations
    # ------------------------------------------------------------------

    def create_user(
        self,
        email: str,
        firstname: str | None,
        lastname: str | None,
        role_ids: list[int],
    ) -> User:
        """Create a new user and optionally assign roles to them.

        Args:
            email: The new user's email address (must be unique).
            firstname: First name (optional).
            lastname: Last name (optional).
            role_ids: IDs of roles to assign immediately upon creation.

        Returns:
            The newly created and refreshed ``User`` instance.

        Raises:
            HTTPException: 409 if a user with the given email already exists.
            HTTPException: 404 if any of the provided ``role_ids`` do not exist.
        """
        user = User(email=email, firstname=firstname, lastname=lastname)
        self._db_session.add(user)
        try:
            self._db_session.flush()
        except IntegrityError as exc:
            self._db_session.rollback()
            logger.warning("Attempted to create duplicate user: %s", email)
            raise HTTPException(
                status_code=409, detail=f"User with email '{email}' already exists."
            ) from exc

        for role_id in role_ids:
            role = self._db_session.get(Role, role_id)
            if role is None:
                self._db_session.rollback()
                raise HTTPException(
                    status_code=404, detail=f"Role with id {role_id} not found."
                )
            user_role = UserRole(user_email=email, role_id=role_id)
            self._db_session.add(user_role)

        self._db_session.commit()
        self._db_session.refresh(user)
        return user

    def bulk_create_users(self, emails: list[str], role_ids: list[int]) -> list[User]:
        """Create multiple users at once, assigning shared roles to all of them.

        Users that already exist are skipped (no error raised for duplicates
        in bulk mode — the existing user is included in the returned list).

        Args:
            emails: List of email addresses to create.
            role_ids: Role IDs to assign to every created user.

        Returns:
            List of ``User`` instances (newly created or pre-existing).

        Raises:
            HTTPException: 404 if any of the provided ``role_ids`` do not exist.
        """
        # Validate roles first
        for role_id in role_ids:
            role = self._db_session.get(Role, role_id)
            if role is None:
                raise HTTPException(
                    status_code=404, detail=f"Role with id {role_id} not found."
                )

        created_users: list[User] = []
        for email in emails:
            existing = self._db_session.get(User, email)
            if existing is not None:
                created_users.append(existing)
                continue

            user = User(email=str(email))
            self._db_session.add(user)
            try:
                self._db_session.begin_nested()
                self._db_session.flush()
            except IntegrityError:
                self._db_session.rollback()
                logger.warning("Skipping duplicate user in bulk create: %s", email)
                existing = self._db_session.get(User, email)
                if existing:
                    created_users.append(existing)
                continue

            for role_id in role_ids:
                user_role = UserRole(user_email=str(email), role_id=role_id)
                self._db_session.add(user_role)

            created_users.append(user)

        self._db_session.commit()
        for user in created_users:
            self._db_session.refresh(user)

        return created_users

    def delete_user(self, email: str) -> bool:
        """Delete a user and all their role assignments.

        Args:
            email: The email address of the user to delete.

        Returns:
            ``True`` if the user was found and deleted, ``False`` if not found.
        """
        user = self._db_session.get(User, email)
        if user is None:
            return False

        # Remove all user_role entries first
        user_roles = self._db_session.exec(
            select(UserRole).where(UserRole.user_email == email)
        ).all()
        for ur in user_roles:
            self._db_session.delete(ur)
        self._db_session.flush()

        self._db_session.delete(user)
        self._db_session.commit()
        return True

    # ------------------------------------------------------------------
    # Role management on users
    # ------------------------------------------------------------------

    def get_user_roles(self, email: str) -> list[Role]:
        """Return the list of roles currently assigned to a user.

        Args:
            email: The user's email address.

        Returns:
            A list of ``Role`` objects assigned to the user (may be empty).
        """
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_email == email)
        )
        return list(self._db_session.exec(stmt).all())

    def assign_roles(
        self, email: str, role_ids: list[int], assigned_by: str | None
    ) -> User:
        """Add roles to a user, preserving any existing role assignments.

        Roles that are already assigned are silently ignored (no duplicate entries).

        Args:
            email: The user's email address.
            role_ids: IDs of roles to add.
            assigned_by: Identifier of the admin performing the assignment (optional).

        Returns:
            The updated ``User`` instance.

        Raises:
            HTTPException: 404 if the user or any specified role does not exist.
        """
        user = self._db_session.get(User, email)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{email}' not found.")

        # Existing role IDs for this user
        existing_role_ids = {
            ur.role_id
            for ur in self._db_session.exec(
                select(UserRole).where(UserRole.user_email == email)
            ).all()
        }

        for role_id in role_ids:
            if role_id in existing_role_ids:
                continue
            role = self._db_session.get(Role, role_id)
            if role is None:
                raise HTTPException(
                    status_code=404, detail=f"Role with id {role_id} not found."
                )
            user_role = UserRole(
                user_email=email, role_id=role_id, assigned_by=assigned_by
            )
            self._db_session.add(user_role)

        self._db_session.commit()
        self._db_session.refresh(user)
        return user

    def replace_roles(
        self, email: str, role_ids: list[int], assigned_by: str | None
    ) -> User:
        """Replace all of a user's roles with the provided list.

        All existing role assignments are removed before the new ones are added.

        Args:
            email: The user's email address.
            role_ids: IDs of roles to assign (replaces all previous roles).
            assigned_by: Identifier of the admin performing the replacement (optional).

        Returns:
            The updated ``User`` instance.

        Raises:
            HTTPException: 404 if the user or any specified role does not exist.
        """
        user = self._db_session.get(User, email)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{email}' not found.")

        # Validate all roles exist before making any changes
        for role_id in role_ids:
            if self._db_session.get(Role, role_id) is None:
                raise HTTPException(
                    status_code=404, detail=f"Role with id {role_id} not found."
                )

        # Remove existing assignments
        existing = self._db_session.exec(
            select(UserRole).where(UserRole.user_email == email)
        ).all()
        for ur in existing:
            self._db_session.delete(ur)
        self._db_session.flush()

        # Add new assignments
        for role_id in role_ids:
            user_role = UserRole(
                user_email=email, role_id=role_id, assigned_by=assigned_by
            )
            self._db_session.add(user_role)

        self._db_session.commit()
        self._db_session.refresh(user)
        return user

    def replace_roles_by_name(
        self,
        email: str,
        role_names: list[str],
        assigned_by: str | None,
        auto_create: bool = True,
    ) -> User:
        """Replace all of a user's roles using role names, optionally creating missing roles.

        Args:
            email: The user's email address.
            role_names: Names of roles to assign (replaces all previous roles).
            assigned_by: Identifier of the admin performing the replacement (optional).
            auto_create: If ``True``, roles that do not yet exist are created automatically.
                         If ``False``, a 404 is raised for any missing role.

        Returns:
            The updated ``User`` instance.

        Raises:
            HTTPException: 404 if the user does not exist, or if a role does not exist
                and ``auto_create`` is ``False``.
        """
        user = self._db_session.get(User, email)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{email}' not found.")

        role_ids: list[int] = []
        for role_name in role_names:
            role = self._db_session.exec(
                select(Role).where(Role.name == role_name)
            ).first()
            if role is None:
                if not auto_create:
                    raise HTTPException(
                        status_code=404, detail=f"Role '{role_name}' not found."
                    )
                role = Role(name=role_name)
                self._db_session.add(role)
                self._db_session.flush()
            role_ids.append(role.id)  # type: ignore[arg-type]

        return self.replace_roles(
            email=email, role_ids=role_ids, assigned_by=assigned_by
        )

    def remove_role(self, email: str, role_id: int) -> bool:
        """Remove a single role assignment from a user.

        Args:
            email: The user's email address.
            role_id: The ID of the role to remove.

        Returns:
            ``True`` if the assignment existed and was removed, ``False`` otherwise.
        """
        stmt = select(UserRole).where(
            UserRole.user_email == email, UserRole.role_id == role_id
        )
        user_role = self._db_session.exec(stmt).first()
        if user_role is None:
            return False
        self._db_session.delete(user_role)
        self._db_session.commit()
        return True

    # ------------------------------------------------------------------
    # Role CRUD
    # ------------------------------------------------------------------

    def get_role(self, role_id: int) -> Role | None:
        """Retrieve a role by its integer ID.

        Args:
            role_id: The role's primary key.

        Returns:
            The ``Role`` instance if found, otherwise ``None``.
        """
        return self._db_session.get(Role, role_id)

    def get_all_roles(self) -> list[Role]:
        """Return all roles in the database, ordered by name.

        Returns:
            A list of all ``Role`` instances.
        """
        return list(self._db_session.exec(select(Role).order_by(Role.name)).all())

    def create_role(self, name: str, description: str | None) -> Role:
        """Create a new role with the given name and optional description.

        Args:
            name: Unique role name.
            description: Optional human-readable description.

        Returns:
            The newly created and refreshed ``Role`` instance.

        Raises:
            HTTPException: 409 if a role with the given name already exists.
        """
        role = Role(name=name, description=description)
        self._db_session.add(role)
        try:
            self._db_session.flush()
        except IntegrityError as exc:
            self._db_session.rollback()
            logger.warning("Attempted to create duplicate role: %s", name)
            raise HTTPException(
                status_code=409, detail=f"Role with name '{name}' already exists."
            ) from exc
        self._db_session.commit()
        self._db_session.refresh(role)
        return role

    def update_role(
        self, role_id: int, name: str | None, description: str | None
    ) -> Role | None:
        """Update an existing role's name and/or description.

        Only provided (non-``None``) fields are updated.

        Args:
            role_id: The ID of the role to update.
            name: New name for the role (``None`` keeps the existing value).
            description: New description (``None`` keeps the existing value).

        Returns:
            The updated ``Role`` instance, or ``None`` if the role was not found.

        Raises:
            HTTPException: 409 if the new name conflicts with an existing role.
        """
        role = self._db_session.get(Role, role_id)
        if role is None:
            return None

        if name is not None:
            role.name = name
        if description is not None:
            role.description = description
        role.updated_at = datetime.now(timezone.utc)

        try:
            self._db_session.flush()
        except IntegrityError as exc:
            self._db_session.rollback()
            raise HTTPException(
                status_code=409, detail=f"Role with name '{name}' already exists."
            ) from exc

        self._db_session.commit()
        self._db_session.refresh(role)
        return role

    def delete_role(self, role_id: int) -> bool:
        """Delete a role after removing all user-role assignments that reference it.

        This method intentionally removes ``UserRole`` entries before deleting the
        ``Role`` to avoid orphan rows (SQLite does not enforce FK constraints by
        default; PostgreSQL would raise an error otherwise).

        Args:
            role_id: The ID of the role to delete.

        Returns:
            ``True`` if the role existed and was deleted, ``False`` if not found.
        """
        role = self._db_session.get(Role, role_id)
        if role is None:
            return False

        # Remove all user_role entries referencing this role
        user_roles = self._db_session.exec(
            select(UserRole).where(UserRole.role_id == role_id)
        ).all()
        for ur in user_roles:
            self._db_session.delete(ur)
        self._db_session.flush()

        self._db_session.delete(role)
        self._db_session.commit()
        return True

    # ------------------------------------------------------------------
    # JWT sync
    # ------------------------------------------------------------------

    def _sync_prefixed_jwt_roles(
        self, email: str, jwt_roles: list[str], role_prefix: str
    ) -> None:
        """Additively assign the prefixed JWT roles to a user.

        Only roles whose name starts with ``role_prefix`` are considered, so
        internally-managed (non-prefixed) roles are never touched. Missing
        ``Role`` rows are created on the fly. This is additive only: roles already
        assigned are left in place and no role is ever removed (revocations made in
        Keycloak are therefore not propagated).

        Args:
            email: The user's email address (must already exist in the DB).
            jwt_roles: Full list of roles present in the JWT token.
            role_prefix: Only roles whose name starts with this prefix are synced.
        """
        prefixed_roles = [r for r in jwt_roles if r.startswith(role_prefix)]
        if not prefixed_roles:
            return

        existing_role_ids = {
            ur.role_id
            for ur in self._db_session.exec(
                select(UserRole).where(UserRole.user_email == email)
            ).all()
        }
        for role_name in prefixed_roles:
            role = self._db_session.exec(
                select(Role).where(Role.name == role_name)
            ).first()
            if role is None:
                role = Role(name=role_name)
                self._db_session.add(role)
                self._db_session.flush()
            if role.id not in existing_role_ids:
                self._db_session.add(UserRole(user_email=email, role_id=role.id))
                existing_role_ids.add(role.id)

    def sync_user_from_jwt(
        self,
        email: str,
        firstname: str | None,
        lastname: str | None,
        jwt_roles: list[str],
        role_prefix: str,
    ) -> User:
        """Synchronise a user record from Keycloak JWT claims.

        Behaviour differs depending on whether the user already exists:

        * **New user**: Creates the ``User`` record and assigns any JWT roles whose
          name starts with ``role_prefix`` (creating the ``Role`` row if needed).
        * **Existing user**: Updates ``firstname``, ``lastname``, and ``last_login_at``,
          then additively assigns any newly granted prefixed JWT roles. Existing
          roles are preserved and none are removed (revocations are not propagated),
          and non-prefixed internally-managed roles are never touched.

        Args:
            email: The user's email address extracted from the JWT.
            firstname: First name from the JWT (``given_name`` claim).
            lastname: Last name from the JWT (``family_name`` claim).
            jwt_roles: Full list of roles present in the JWT token.
            role_prefix: Only roles whose name starts with this prefix are synced
                to the DB.

        Returns:
            The created or updated ``User`` instance.
        """
        existing = self._db_session.get(User, email)
        now = datetime.now(timezone.utc)

        if existing is None:
            # New user: create + sync roles from JWT
            user = User(
                email=email, firstname=firstname, lastname=lastname, last_login_at=now
            )
            self._db_session.add(user)
            self._db_session.flush()

            self._sync_prefixed_jwt_roles(email, jwt_roles, role_prefix)

            self._db_session.commit()
            self._db_session.refresh(user)
        else:
            # Existing user: update name/login timestamp and additively sync roles
            if firstname:
                existing.firstname = firstname
            if lastname:
                existing.lastname = lastname
            existing.last_login_at = now
            existing.updated_at = now

            self._sync_prefixed_jwt_roles(email, jwt_roles, role_prefix)

            self._db_session.commit()
            self._db_session.refresh(existing)
            user = existing

        return user
