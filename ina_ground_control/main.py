"""
Ground control application, including routes, middleware, and configuration.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi_keycloak_middleware import (
    AuthorizationMethod,
    KeycloakConfiguration,
    setup_keycloak_middleware,
)

from ina_ground_control import get_engine, logger, settings
from ina_ground_control.constants.roles import GROUND_CONTROL, Permission
from ina_ground_control.exception.exceptions import (
    GroundControlException,
    GroundControlRequestValidationError,
)
from ina_ground_control.exception.handlers import default_exception_handler
from ina_ground_control.ina_user_admin import create_user_mapper, setup_user_admin
from ina_ground_control.ina_user_admin.config import UserAdminSettings
from ina_ground_control.routers import (
    annotations,
    management,
    medias,
    plugins,
    projects,
    resources,
    steps,
    tags,
    task_comments,
    tasks,
    users,
)
from ina_ground_control.services.telemetry_service import TelemetryService
from ina_ground_control.utils.application_helpers import mount_static_directory
from ina_ground_control.utils.prometheus import PrometheusMiddleware

app = FastAPI(
    title=settings.application,
    version=settings.version,
    openapi_url=f"{settings.api_docs_path}/openapi.json",
    debug=settings.debug,
)

# 1.auth Load settings from environment variables (USER_ADMIN_ prefix)
settings_auth = UserAdminSettings(
    app_name=settings.application,
    role_prefix=GROUND_CONTROL,
    admin_permission=Permission.ACCESS_CONTROL.value,
    database_url=(
        f"{settings.db_server}://{settings.db_username}:{settings.db_password}"
        f"@{settings.db_hostname}:{settings.db_port}/{settings.db_database}"
    ),
    keycloak_url=settings.sso_url,
    keycloak_realm=settings.sso_realm,
    keycloak_client_id=settings.sso_client_id,
    router_prefix="",  # adjust if your API is mounted under a prefix
    create_tables=False,  # set False in production if using Alembic
    auto_create_user=True,  # Auto create user
)
setup_user_admin(app, settings_auth)

# Set up Keycloak
keycloak_config = KeycloakConfiguration(
    url=settings.sso_url,
    realm=settings.sso_realm,
    client_id=settings.sso_client_id,
    client_secret=settings.sso_client_secret,
    claims=[
        "sub",
        "email",
        "given_name",
        "family_name",
        "preferred_username",
        "roles",
        "openid",
    ],
    reject_on_missing_claim=False,
    verify=True,
    authorization_method=AuthorizationMethod.CLAIM,
    authorization_claim="roles",
    use_introspection_endpoint=False,
    swagger_client_id=settings.sso_client_id,
    # jwcrypto: fournir check_claims desactive le controle par defaut de exp,
    # il faut donc le redeclarer (None = claim requis, valeur temporelle verifiee)
    validation_options=(
        {"check_claims": {"exp": None, "aud": settings.sso_audience}}
        if settings.sso_verify_aud
        else {}
    ),
)

setup_keycloak_middleware(
    app,
    keycloak_configuration=keycloak_config,
    exclude_patterns=[
        "/management/*",
        "/docs",
        "/gen_docs/*",
        "/openapi.json",
        "/redoc",
        "/static/*",
    ],
    user_mapper=create_user_mapper(app),
)

# Add router
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(annotations.router)
app.include_router(resources.router)
app.include_router(medias.router)
app.include_router(plugins.router)
app.include_router(steps.router)
app.include_router(tags.router)
app.include_router(task_comments.router)
app.include_router(management.router)
# Setting metrics middleware
app.add_middleware(PrometheusMiddleware, app_name=settings.application)

# Mount the static directories
mount_static_directory(app, "/static", "static", "static")
app.servers = [
    {"url": f"http://{settings.server_host}:{settings.server_port}"}  # NOSONAR
]

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers,
)


@app.middleware("http")
async def log_user(request: Request, call_next):
    # Add user email to the log record
    response = await call_next(request)
    user = request.scope.get("user", {})
    if isinstance(user, dict):
        user_email = user.get("email", "Unknown")
    else:
        user_email = user.email
    user_logger = logging.getLogger("uvicorn.debug")
    user_logger.info("User: %s", user_email)
    return response


app.add_exception_handler(GroundControlException, default_exception_handler)
app.add_exception_handler(
    GroundControlRequestValidationError, default_exception_handler
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        "422 Unprocessable Entity on %s %s — errors: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    try:
        # Generate the base schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Add components if missing
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        # Add securitySchemes if missing
        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}

        # Add custom openId security scheme
        openapi_schema["components"]["securitySchemes"]["openid"] = {
            "type": "openIdConnect",
            "openIdConnectUrl": settings.sso_url
            + "/realms/"
            + settings.sso_realm
            + "/.well-known/openid-configuration",
        }

        # Apply openId securitySchemes on every routes
        openapi_schema["security"] = [{"openid": ["admin"]}]

        app.openapi_schema = openapi_schema  # Cache the schema
        return app.openapi_schema
    except Exception as e:
        logger.error("Error generating OpenAPI schema: %s", str(e))
        raise


app.openapi = custom_openapi  # type: ignore[method-assign]
# Initialize Telemetry Service
telemetry = TelemetryService(
    app, sql_alchemy_engine=get_engine(str(settings.get_db_connection_string()))
)
