"""
Ground control application, including routes, middleware, and configuration.
"""
import os
import time
import typing
from urllib.request import Request

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_keycloak_middleware import (
    KeycloakConfiguration,
    setup_keycloak_middleware,
    AuthorizationMethod
)

from ina_ground_control import logger
from ina_ground_control.config import settings
from ina_ground_control.models.user_model import UserInfo
from ina_ground_control.routers import projects, tasks, users, resources, annotations, medias, steps, tags, \
    task_comments, plugins, management
from ina_ground_control.services.telemetry_service import TelemetryService


async def map_user(userinfo: typing.Dict[str, typing.Any]) -> UserInfo:
    """
    Maps user information received from Keycloak to a User model instance.

    Args:
        userinfo (Dict[str, Any]): The user information dictionary.

    Returns:
        UserInfo: An instance of the UserInfo model.
    """

    # Map the fields from the userinfo to the UserInfo model
    unk_email = "unknown@unknown.com"
    if userinfo is not None:
        user = UserInfo(
            email=userinfo.get("email", unk_email),
            roles=userinfo.get("roles", []),
        )
    else:
        logger.warning("Userinfo is none check sso has userinfo enabled and token has roles: %s", userinfo)
        user = UserInfo(
            email=unk_email,
            roles=[]
        )
    return user


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

app = FastAPI()
setup_keycloak_middleware(
    app,
    keycloak_configuration=keycloak_config,
    exclude_patterns=["/management/*", "/docs", "/openapi.json", "/redoc"],
    add_swagger_auth=True,
    user_mapper=map_user
)
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
app.servers = [{"url": "http://localhost:8000"}]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization", "Link", "X-Total-Count", "Highlighted"]
)

# Initialize Telemetry Service
telemetry = TelemetryService(app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to capture metrics."""
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    telemetry.record_metrics(request, latency, response.status_code)
    return response


load_dotenv(".env.local")
APP_HOST = os.getenv("APP_HOST")
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL")

if __name__ == "__main__":
    logger.info("Starting server with host: %s and log level: %s", APP_HOST, APP_LOG_LEVEL)
    uvicorn.run("ina_ground_control.main:app", host=APP_HOST, port=8000, log_level=APP_LOG_LEVEL, reload=True)
