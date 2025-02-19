"""
This module sets up the main FastAPI application, including routes, middleware, and configuration.
"""
import os
from dotenv import load_dotenv
import uvicorn
import typing
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_keycloak_middleware import (
    KeycloakConfiguration,
    setup_keycloak_middleware,
    AuthorizationMethod,
    MatchStrategy,
    require_permission,
    CheckPermissions,
    AuthorizationResult
)
from ina_ground_control.config import settings
from ina_ground_control.models.user_model import UserInfo
from ina_ground_control.routers import projects, tasks, users, resources, annotations,medias ,steps,tags,task_comments, plugins
from ina_ground_control.constants.roles import Role, ROLE_PERMISSIONS

async def map_user(userinfo: typing.Dict[str, typing.Any]) -> UserInfo:
    """
    Maps user information received from Keycloak to a User model instance.

    Args:
        userinfo (Dict[str, Any]): The user information dictionary.

    Returns:
        UserInfo: An instance of the UserInfo model.
    """
    print("*********************************************************",userinfo)  # Debugging the userinfo dict

    # Map the fields from the userinfo to the UserInfo model
    user = UserInfo(
        email=userinfo.get("email"),
        roles=userinfo.get("roles", []),
    )

    return user

# Set up Keycloak
keycloak_config = KeycloakConfiguration(
    url=settings.sso.url,
    realm=settings.sso.realm,
    client_id=settings.sso.client_id,
    client_secret=settings.sso.client_secret,
    claims=["openid","email","profile","roles"],
    reject_on_missing_claim=False,
    verify=True,
    validate_token=True,
    authorization_method= AuthorizationMethod.CLAIM,
    authorization_claim="roles",
    use_introspection_endpoint=False,
    swagger_client_id="web_app",
    swagger_auth_scopes=["openid"],  # Optional
    swagger_auth_pkce=True,  # Optional
    swagger_scheme_name="openid",
    decode_options={
        "verify_signature": False,
        "verify_aud": False,
        "verify_exp": True,
    },
)

app = FastAPI()

NO_AUTH = os.getenv("NO_AUTH") != "False"

# Add middleware with basic config
if not NO_AUTH:
    setup_keycloak_middleware(
        app,
        keycloak_configuration=keycloak_config,
        exclude_patterns=["/management/*", "/docs", "/openapi.json", "/redoc"],
        add_swagger_auth=True,
        user_mapper=map_user
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
app.include_router(medias.router)
app.include_router(plugins.router)
app.include_router(steps.router)
app.include_router(tags.router)
app.include_router(task_comments.router)
app.servers = [{"url": "http://localhost:8000"}]

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

@app.get("/admin")
def check_admin(request: Request,authorization_result: AuthorizationResult = Depends(CheckPermissions( ROLE_PERMISSIONS[Role.GC_ADMIN], match_strategy=MatchStrategy.AND))):
    roles_from_token = request.scope.get("auth", {})
    return {"message": "Hello Admin",
            "checked roles": ROLE_PERMISSIONS[Role.GC_ADMIN],
            "roles from token": roles_from_token }


load_dotenv(".env.local")
APP_HOST = os.getenv("APP_HOST")
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL")

if __name__ == "__main__":
    uvicorn.run("ina_ground_control.main:app", host=APP_HOST, port=8000,log_level=APP_LOG_LEVEL, reload=True )
