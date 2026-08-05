from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RoleResponse(BaseModel):
    """Response schema for a role.

    Attributes:
        id: The role's integer primary key.
        name: The unique role name.
        description: Optional human-readable description.
        created_at: When the role was created.
        updated_at: When the role was last updated.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserInfoResponse(BaseModel):
    """Lightweight user info response without role details.

    Attributes:
        email: The user's email address (primary key).
        firstname: The user's first name.
        lastname: The user's last name.
        is_active: Whether the user account is active.
    """

    model_config = ConfigDict(from_attributes=True)

    email: str
    firstname: str | None = None
    lastname: str | None = None
    is_active: bool = True


class UserWithRolesResponse(BaseModel):
    """Full user response including assigned roles and timestamps.

    Attributes:
        sub: OIDC subject identifier (from the JWT ``sub`` claim).
        email: The user's email address (primary key).
        firstname: The user's first name.
        lastname: The user's last name.
        is_active: Whether the user account is active.
        created_at: When the user record was created.
        updated_at: When the user record was last updated.
        last_login_at: Timestamp of the user's most recent login.
        roles: List of roles assigned to this user.
    """

    model_config = ConfigDict(from_attributes=True)

    sub: str | None = None
    email: str
    firstname: str | None = None
    lastname: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
    roles: list[RoleResponse] = []


class CreateUserRequest(BaseModel):
    """Request schema for creating a single user.

    Attributes:
        email: The user's email address (will become the primary key).
        firstname: The user's first name (optional).
        lastname: The user's last name (optional).
        role_ids: List of role IDs to assign to the user on creation.
    """

    email: EmailStr
    firstname: str | None = None
    lastname: str | None = None
    role_ids: list[int] = []


class BulkCreateUsersRequest(BaseModel):
    """Request schema for bulk-creating multiple users with shared roles.

    Attributes:
        emails: List of email addresses to create as users.
        role_ids: Role IDs to assign to all created users.
    """

    emails: list[EmailStr]
    role_ids: list[int] = []


class PaginatedUsersResponse(BaseModel):
    """Paginated response wrapper for user listings.

    Attributes:
        items: The list of users on the current page.
        total: Total number of users matching the query.
        page: The current page index (0-based).
        page_size: Number of items per page.
        total_pages: Total number of pages.
    """

    model_config = ConfigDict(from_attributes=True)

    items: list[UserWithRolesResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CreateRoleRequest(BaseModel):
    """Request schema for creating a new role.

    Attributes:
        name: The unique role name (e.g. ``app:resource:action``).
        description: Optional human-readable description of the role.
    """

    name: str
    description: str | None = None


class UpdateRoleRequest(BaseModel):
    """Request schema for updating an existing role.

    All fields are optional; only provided fields are updated.

    Attributes:
        name: New role name (optional).
        description: New description (optional).
    """

    name: str | None = None
    description: str | None = None


class AssignRolesRequest(BaseModel):
    """Request schema for assigning roles to a user by role ID.

    Attributes:
        role_ids: List of role IDs to assign.
    """

    role_ids: list[int]


class AssignRolesByNameRequest(BaseModel):
    """Request schema for replacing a user's roles by name.

    Missing roles are automatically created. This endpoint is intended for
    administrative bulk operations where role names are known but IDs are not.

    Attributes:
        role_names: List of role names to assign. Roles that do not exist will
            be created automatically.
    """

    role_names: list[str]
