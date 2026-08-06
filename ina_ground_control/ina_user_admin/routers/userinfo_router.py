"""APIRouter exposing the OIDC-style ``/userinfo`` endpoint."""

from fastapi import APIRouter, HTTPException, Request

from ina_ground_control.ina_user_admin.schemas import (
    RoleResponse,
    UserWithRolesResponse,
)


def create_userinfo_router() -> APIRouter:
    """Create and return the ``/userinfo`` APIRouter.

    The returned router exposes a single ``GET /userinfo`` endpoint that any
    authenticated user can call to retrieve their own profile and DB-sourced roles.

    Returns:
        A configured ``APIRouter`` instance ready to be included in a FastAPI app.
    """
    router = APIRouter()

    @router.get("/userinfo", response_model=UserWithRolesResponse)
    async def get_userinfo(request: Request) -> UserWithRolesResponse:
        """Get current user info including DB roles (OIDC-compliant).

        Reads the authenticated user from ``request.scope["user"]`` (populated by
        ``map_user_from_jwt``) and returns their profile together with the roles
        stored in the database.

        Args:
            request: The current FastAPI request.

        Returns:
            A ``UserWithRolesResponse`` containing the user's profile and roles.

        Raises:
            HTTPException: 401 if no authenticated user is found in the request scope.
        """
        user = request.scope.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        roles: list[RoleResponse] = []
        for r in getattr(user, "roles", None) or []:
            if hasattr(r, "name"):
                roles.append(RoleResponse.model_validate(r))
            else:
                roles.append(
                    RoleResponse(
                        id=None,
                        name=str(r),
                        description=None,
                        created_at=None,
                        updated_at=None,
                    )
                )

        return UserWithRolesResponse(
            sub=getattr(user, "sub", None),
            email=user.email,
            firstname=getattr(user, "firstname", None),
            lastname=getattr(user, "lastname", None),
            is_active=getattr(user, "is_active", True),
            created_at=getattr(user, "created_at", None),
            updated_at=getattr(user, "updated_at", None),
            last_login_at=getattr(user, "last_login_at", None),
            roles=roles,
        )

    return router
