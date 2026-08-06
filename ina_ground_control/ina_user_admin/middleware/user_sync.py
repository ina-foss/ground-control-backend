"""Synchronisation of authenticated JWT users into the local database."""

import logging
from datetime import datetime

from fastapi import Request
from sqlmodel import Session, select

from ina_ground_control.ina_user_admin.repository import UserRepository
from ina_ground_control.models.role import Role
from ina_ground_control.models.user_model import User
from ina_ground_control.models.user_role import UserRole

logger = logging.getLogger(__name__)


class _SyncedUser:
    """Lightweight user object placed into ``request.scope["user"]`` after JWT sync.

    Attributes:
        sub: OIDC subject identifier from the JWT.
        email: The user's email address.
        firstname: First name from the JWT or DB.
        lastname: Last name from the JWT or DB.
        is_active: Whether the user account is active.
        roles: List of ``Role`` objects loaded from the database.
        created_at: When the user record was created in the DB.
        updated_at: When the user record was last updated.
        last_login_at: Timestamp of the user's most recent login.
    """

    def __init__(
        self,
        email: str,
        firstname: str | None,
        lastname: str | None,
        is_active: bool,
        roles: list[Role],
        sub: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_login_at: datetime | None = None,
    ) -> None:
        self.sub = sub
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.is_active = is_active
        self.roles = roles
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_login_at = last_login_at


async def map_user_from_jwt(request: Request, user_info: object) -> _SyncedUser:
    """Map a Keycloak OIDC user to a DB-synced user object.

    This function is intended to be passed as the ``user_mapper`` callable to
    ``fastapi-keycloak-middleware``. It calls
    ``UserRepository.sync_user_from_jwt()`` on every authenticated request to:

    * Create a new DB user for first-time logins (syncing prefixed JWT roles).
    * Update name / last-login timestamp for returning users (DB roles unchanged).

    The returned ``_SyncedUser`` is stored in ``request.scope["user"]`` and
    subsequently read by ``CheckPermissionsFromDB``.

    Args:
        request: The FastAPI request; used to access ``app.state``.
        user_info: The ``OIDCUser`` object provided by ``fastapi-keycloak-middleware``.

    Returns:
        A ``_SyncedUser`` instance with DB roles eagerly loaded.
    """
    settings = request.app.state.user_admin_settings
    engine = request.app.state.user_admin_engine
    unk_email = "unknown@unknown.com"

    sub = getattr(user_info, "sub", None)
    firstname = getattr(user_info, "given_name", None)
    lastname = getattr(user_info, "family_name", None)
    sub = getattr(user_info, "sub", None)
    preferred_username = getattr(user_info, "preferred_username", None) or getattr(
        user_info, "client_id", "unknown"
    )

    email = getattr(user_info, "email", None) or f"{preferred_username}@unknown.com"

    if not firstname:
        firstname = email.split("@")[0] if email != unk_email else "Unknown"
    if not lastname:
        lastname = ""

    jwt_roles: list[str] = []
    if hasattr(user_info, "roles"):
        raw = user_info.roles  # type: ignore[union-attr]
        jwt_roles = list(raw) if raw else []

    with Session(engine) as session:
        repo = UserRepository(session)
        repo.sync_user_from_jwt(
            email=email,
            firstname=firstname,
            lastname=lastname,
            jwt_roles=jwt_roles,
            role_prefix=settings.role_prefix,
        )

        # Eagerly load the user and their roles to avoid detached-instance issues
        # after the session closes.
        db_user = session.exec(select(User).where(User.email == email)).first()
        roles = list(
            session.exec(
                select(Role)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(UserRole.user_email == email)
            ).all()
        )

    return _SyncedUser(
        email=email,
        firstname=firstname,
        lastname=lastname,
        is_active=db_user.is_active if db_user else True,
        roles=roles,
        sub=sub,
        created_at=db_user.created_at if db_user else None,
        updated_at=db_user.updated_at if db_user else None,
        last_login_at=db_user.last_login_at if db_user else None,
    )
