"""Pydantic schemas (DTOs) for ina-user-admin request/response bodies."""

from ina_ground_control.ina_user_admin.schemas.permission import PermissionDTO
from ina_ground_control.ina_user_admin.schemas.user import (
    AssignRolesByNameRequest,
    AssignRolesRequest,
    BulkCreateUsersRequest,
    CreateRoleRequest,
    CreateUserRequest,
    PaginatedUsersResponse,
    RoleResponse,
    UpdateRoleRequest,
    UserInfoResponse,
    UserWithRolesResponse,
)

__all__ = [
    "RoleResponse",
    "UserInfoResponse",
    "UserWithRolesResponse",
    "CreateUserRequest",
    "BulkCreateUsersRequest",
    "PaginatedUsersResponse",
    "CreateRoleRequest",
    "UpdateRoleRequest",
    "AssignRolesRequest",
    "AssignRolesByNameRequest",
    "PermissionDTO",
]
