"""ina-user-admin — plug-and-play user administration for INA FastAPI projects.

The single integration point is :func:`setup_user_admin`. Consumer projects call
this once during application startup to register all user/role endpoints and
initialise the database engine.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Coroutine

from fastapi import FastAPI
from sqlmodel import Session, SQLModel, create_engine, select

# Import models so that SQLModel.metadata is populated (required for create_all / Alembic)
import ina_ground_control.models  # noqa: F401
from ina_ground_control.ina_user_admin.config import UserAdminSettings
from ina_ground_control.ina_user_admin.middleware.user_sync import _SyncedUser
from ina_ground_control.ina_user_admin.repository import UserRepository
from ina_ground_control.ina_user_admin.routers import (
    create_user_router,
    create_userinfo_router,
)
from ina_ground_control.models.role import Role
from ina_ground_control.models.user_model import User
from ina_ground_control.models.user_role import UserRole

logger = logging.getLogger(__name__)


def setup_user_admin(app: FastAPI, settings: UserAdminSettings) -> None:
    """Register user admin routers and initialise the database engine on the FastAPI app.

    Stores ``settings`` and the SQLAlchemy ``engine`` in ``app.state`` so that
    FastAPI dependencies can access them per-request without global variables.

    After calling this function the following routes are available (prefixed by
    ``settings.router_prefix``):

    * ``GET  /userinfo`` — authenticated user's profile + DB roles
    * ``GET  /users`` — paginated user list (admin only)
    * ``POST /users`` — create user (admin only)
    * … (see router files for full list)

    Args:
        app: The FastAPI application instance to attach the routers to.
        settings: Fully configured ``UserAdminSettings`` instance. All configuration
            (Keycloak URLs, admin permission name, DB URL, etc.) is sourced from here —
            nothing is hardcoded.
    """
    engine = create_engine(settings.database_url)
    app.state.user_admin_settings = settings
    app.state.user_admin_engine = engine

    if settings.create_tables:
        SQLModel.metadata.create_all(engine)
        logger.info("ina-user-admin: database tables created/verified")

    user_router = create_user_router()
    userinfo_router = create_userinfo_router()

    app.include_router(
        user_router, prefix=settings.router_prefix, tags=settings.router_tags
    )
    app.include_router(
        userinfo_router, prefix=settings.router_prefix, tags=settings.router_tags
    )


def create_user_mapper(
    app: FastAPI,
) -> Callable[[dict[str, Any]], Coroutine[Any, Any, Any]]:
    """Create a user mapper function compatible with ``fastapi-keycloak-middleware``.

    Returns an async callable with signature ``(userinfo: dict) -> _SyncedUser``
    that can be passed directly as the ``user_mapper`` parameter to
    ``setup_keycloak_middleware``.

    When ``settings.auto_create_user`` is ``True`` (default), new users are
    automatically created in the database on first login. When ``False``, only
    existing users are synced.

    Args:
        app: The FastAPI app (must have been passed to ``setup_user_admin`` first).

    Returns:
        An async user mapper function.
    """

    async def _mapper(userinfo: dict[str, Any]) -> _SyncedUser | None:
        if not isinstance(userinfo, dict) or not userinfo:
            return None

        settings: UserAdminSettings = app.state.user_admin_settings
        engine = app.state.user_admin_engine
        unk_email = "unknown@unknown.com"

        sub = userinfo.get("sub")
        firstname = userinfo.get("given_name", "")
        lastname = userinfo.get("family_name", "")
        jwt_roles = userinfo.get("roles") or []
        preferred_username = userinfo.get(
            "preferred_username",
            userinfo.get("preferred_username", userinfo.get("client_id", "unknown")),
        )
        email = userinfo.get("email", preferred_username + "@unknown.com")

        if not firstname:
            firstname = email.split("@")[0] if email != unk_email else "Unknown"
        if not lastname:
            lastname = ""

        with Session(engine) as session:
            repo = UserRepository(session)

            if settings.auto_create_user:
                repo.sync_user_from_jwt(
                    email=email,
                    firstname=firstname,
                    lastname=lastname,
                    jwt_roles=jwt_roles,
                    role_prefix=settings.role_prefix,
                )
            else:
                existing = session.get(User, email)
                if existing is None:
                    logger.warning(
                        "User %s not found in DB and auto_create_user is disabled",
                        email,
                    )
                    return None

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

    return _mapper
