import logging
from enum import Enum

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


class MatchStrategy(str, Enum):
    """Strategy used when checking multiple required permissions.

    Attributes:
        AND: All required permissions must be present (intersection).
        OR: At least one required permission must be present (union).
    """

    AND = "AND"
    OR = "OR"


class AuthorizationResult:
    """Result returned by a successful ``CheckPermissionsFromDB`` check.

    Attributes:
        user: The authenticated user object from ``request.scope["user"]``.
        matched_permissions: The subset of required permissions that were found
            in the user's DB roles.
    """

    def __init__(self, user: object, matched_permissions: list[str]) -> None:
        """Initialise the result.

        Args:
            user: The user object from the request scope.
            matched_permissions: Permissions that matched the user's roles.
        """
        self.user = user
        self.matched_permissions = matched_permissions


class CheckPermissionsFromDB:
    """FastAPI dependency that verifies the authenticated user holds the required DB roles.

    Reads roles from ``request.scope["user"].roles`` (set by ``map_user_from_jwt``),
    **not** from the raw JWT. This allows role management via the admin UI without
    requiring Keycloak group changes.

    Usage::

        @router.get("/admin-only")
        async def admin_endpoint(
            auth: AuthorizationResult = Depends(CheckPermissionsFromDB(["app:admin"])),
        ):
            ...

    Attributes:
        required_permissions: Permission names that are checked against the user's roles.
        strategy: Whether ALL or ANY of the required permissions must be present.
    """

    def __init__(
        self,
        required_permissions: list[str],
        strategy: MatchStrategy = MatchStrategy.OR,
    ) -> None:
        """Configure the permission check.

        Args:
            required_permissions: List of role/permission names to require.
            strategy: ``MatchStrategy.OR`` (default) or ``MatchStrategy.AND``.
        """
        self.required_permissions = required_permissions
        self.strategy = strategy

    async def __call__(self, request: Request) -> AuthorizationResult:
        """Execute the permission check for an incoming request.

        Args:
            request: The current FastAPI ``Request`` object.

        Returns:
            An ``AuthorizationResult`` containing the user and matched permissions.

        Raises:
            HTTPException: 401 if no user is present in the request scope.
            HTTPException: 403 if the user does not satisfy the permission requirements.
        """
        user = request.scope.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if hasattr(user, "is_active") and not user.is_active:
            raise HTTPException(status_code=403, detail="User account is deactivated")

        user_roles = [r.name if hasattr(r, "name") else r for r in (getattr(user, "roles", None) or [])]

        matched = [p for p in self.required_permissions if p in user_roles]

        if self.strategy == MatchStrategy.AND:
            if len(matched) < len(self.required_permissions):
                missing = set(self.required_permissions) - set(matched)
                logger.warning("User %s missing permissions: %s", getattr(user, "email", "?"), missing)
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        else:  # OR — empty requirements list means "no restriction"
            if self.required_permissions and not matched:
                logger.warning(
                    "User %s has none of required permissions: %s",
                    getattr(user, "email", "?"),
                    self.required_permissions,
                )
                raise HTTPException(status_code=403, detail="Insufficient permissions")

        return AuthorizationResult(user=user, matched_permissions=matched)


async def get_auth_from_db(request: Request) -> object:
    """FastAPI dependency that validates a user is authenticated (no permission check).

    Simply confirms that ``request.scope["user"]`` has been populated by the
    Keycloak middleware / ``map_user_from_jwt``. Does not inspect roles.

    Args:
        request: The current FastAPI ``Request`` object.

    Returns:
        The user object from ``request.scope["user"]``.

    Raises:
        HTTPException: 401 if no user is present in the request scope.
    """
    user = request.scope.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
