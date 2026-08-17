"""Settings model for the ina-user-admin package."""

from pydantic_settings import BaseSettings


class UserAdminSettings(BaseSettings):
    """Configuration for the ina-user-admin package.

    All settings can be provided via environment variables with the USER_ADMIN_ prefix.

    Attributes:
        app_name: The name of the consuming application (e.g. "toolbox-ia").
        role_prefix: Prefix used to filter JWT roles for sync (e.g. "toolbox-ia").
        keycloak_url: Base URL of the Keycloak server.
        keycloak_realm: Keycloak realm name.
        keycloak_client_id: Keycloak client ID for this application.
        database_url: SQLAlchemy database connection string.
        admin_permission: The role name that grants full admin access to user management endpoints.
        router_prefix: URL prefix for all user admin routes (e.g. "/api").
        router_tags: OpenAPI tags applied to all user admin routes.
    """

    # Identity
    app_name: str
    role_prefix: str

    # Keycloak
    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str

    # Database
    database_url: str

    # Admin role
    admin_permission: str

    # Behaviour
    auto_create_user: bool = True
    create_tables: bool = False

    # Router config
    router_prefix: str = ""
    router_tags: list[str] = ["Users"]

    model_config = {"env_prefix": "USER_ADMIN_"}
