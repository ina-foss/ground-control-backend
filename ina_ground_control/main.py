"""
This module sets up the main FastAPI application, including routes, middleware, and configuration.
"""
import uvicorn
import typing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_keycloak_middleware import (
    KeycloakConfiguration,
    setup_keycloak_middleware,
    AuthorizationMethod,
)
from ina_ground_control.config import settings
from ina_ground_control.models.user_model import User
from ina_ground_control.routers import projects, tasks, users, resources, annotations


async def map_user(userinfo: typing.Dict[str, typing.Any]) -> User:
    """
    Maps user information received from Keycloak to a User model instance.

    Args:
        userinfo (Dict[str, Any]): The user information dictionary.

    Returns:
        User: An instance of the User model.
    """
    # Do something with the userinfo
    print(userinfo)
    return User()

# Set up Keycloak
keycloak_config = KeycloakConfiguration(
    url=settings.sso.url,
    realm=settings.sso.realm,
    client_id=settings.sso.client_id,
    client_secret=settings.sso.client_secret,
    reject_on_missing_claim=True,
    verify=True,
    validate_token=True,
    authorization_method=AuthorizationMethod.CLAIM,
    authorization_claim="roles",
    use_introspection_endpoint=False,
    swagger_client_id="web_app",
    swagger_auth_scopes=["openid"],  # Optional
    swagger_auth_pkce=True,  # Optional
    swagger_scheme_name="openid",
    decode_options={
        "verify_signature": True,
        "verify_aud": False,
        "verify_exp": True,
    },
)

app = FastAPI()

# Add middleware with basic config
setup_keycloak_middleware(
    app,
    keycloak_configuration=keycloak_config,
    exclude_patterns=["/management/*", "/docs", "/openapi.json", "/redoc"],
    add_swagger_auth=True,
)


@app.get("/test")
async def root() -> dict:
    """
    Root endpoint that returns a simple message.

    Returns:
        dict: A dictionary with a greeting message.
    """
    return {"message": "Hello World"}


app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(annotations.router)
app.include_router(resources.router)
#app.servers = [{"url": "http://localhost:8000"}]

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://frontend:3000",
    "https://frontend:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/management/health")
async def info() -> dict:
    """
    Health check endpoint that returns the status of the service.

    Returns:
        dict: A dictionary indicating the service status.
    """
    return {"status": "up"}

if __name__ == "__main__":
    uvicorn.run("ina_ground_control.main:app", host="0.0.0.0", port=8000,log_level="debug", reload=True )
