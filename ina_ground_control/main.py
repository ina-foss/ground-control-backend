"""
Ground control application, including routes, middleware, and configuration.
"""
import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi_keycloak_middleware import (
    KeycloakConfiguration,
    setup_keycloak_middleware,
    AuthorizationMethod
)
from starlette.staticfiles import StaticFiles

from ina_ground_control import logger, get_application_version, map_user
from ina_ground_control.config import settings
from ina_ground_control.database import engine
from ina_ground_control.routers import projects, tasks, users, resources, annotations, medias, steps, tags, \
    task_comments, plugins, management
from ina_ground_control.services.telemetry_service import TelemetryService
from ina_ground_control.utils.prometheus import PrometheusMiddleware
from ina_ground_control.exception.handlers import default_exception_handler
from ina_ground_control.exception.exceptions import GroundControlException, GroundControlRequestValidationError

load_dotenv(".env.local")
app = FastAPI(
    title=settings.app.service_name,
    version=get_application_version(),
    description=settings.app.description,
)
# Set up Keycloak
keycloak_config = KeycloakConfiguration(
    url=settings.sso.url,
    realm=settings.sso.realm,
    client_id=settings.sso.client_id,
    client_secret=settings.sso.client_secret,
    claims=["openid", "email", "profile", "roles"],
    reject_on_missing_claim=False,
    verify=True,
    authorization_method=AuthorizationMethod.CLAIM,
    authorization_claim="roles",
    use_introspection_endpoint=False,
    swagger_client_id=settings.sso.client_id,
    decode_options={
        "verify_signature": True,
        "verify_aud": False,
        "verify_exp": True,
    },
)

setup_keycloak_middleware(
    app,
    keycloak_configuration=keycloak_config,
    exclude_patterns=["/management/*", "/docs", "/gen_docs/*", "/openapi.json", "/redoc", "/static/*"],
    user_mapper=map_user
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
app.add_middleware(PrometheusMiddleware, app_name=settings.app.service_name)
# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/gen_docs", StaticFiles(directory="docs/_build"), name="gen_docs")
app.servers = [{"url": settings.app.server}]

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    expose_headers=settings.cors.expose_headers
)



@app.middleware("http")
async def log_user(request: Request, call_next):
    # Add user email to the log record
    response = await call_next(request)
    user = request.scope.get("user", {})
    user_email = user.email
    user_logger = logging.getLogger("uvicorn.debug")
    user_logger.info("User: %s",user_email)
    return response


app.add_exception_handler(GroundControlException, default_exception_handler)
app.add_exception_handler(GroundControlRequestValidationError, default_exception_handler)

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

        # Add custom OAuth2 security scheme
        openapi_schema["components"]["securitySchemes"]["OAuth2ClientCredentials"] = {
            "type": "oauth2",
            "flows": {
                "clientCredentials": {
                    "tokenUrl": f"{settings.sso.url}realms/{settings.sso.realm}/protocol/openid-connect/token",
                    "scopes": {}
                }
            }
        }

        app.openapi_schema = openapi_schema  # Cache the schema
        return app.openapi_schema
    except Exception as e:
        logger.error("Error generating OpenAPI schema: %s", str(e))
        raise


app.openapi = custom_openapi
# Initialize Telemetry Service
telemetry = TelemetryService(app, engine)

APP_HOST = os.getenv("APP_HOST")
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL")

if __name__ == "__main__":
    logger.info("Starting server with host: %s and log level: %s", APP_HOST, APP_LOG_LEVEL)
    uvicorn.run("ina_ground_control.main:app", host=APP_HOST, port=8000, log_level=APP_LOG_LEVEL, reload=True)
