"""FastAPI routers for ina-user-admin."""

from ina_ground_control.ina_user_admin.routers.user_router import create_user_router
from ina_ground_control.ina_user_admin.routers.userinfo_router import (
    create_userinfo_router,
)

__all__ = ["create_user_router", "create_userinfo_router"]
