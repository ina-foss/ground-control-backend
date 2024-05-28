import typing

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_keycloak_middleware import KeycloakConfiguration, setup_keycloak_middleware, AuthorizationMethod, \
    KeycloakMiddleware
from src.config import settings

from src.models.user_model import User
from src.routers import projects, tasks, users, resources


async def map_user(userinfo: typing.Dict[str, typing.Any]) -> User:
    # Do something with the userinfo
    print(userinfo)
    return User()


# Set up Keycloak
keycloak_config = KeycloakConfiguration(
    url=settings.keycloak.url,
    realm=settings.keycloak.realm,
    client_id=settings.keycloak.client_id,
    client_secret=settings.keycloak.client_secret,
    reject_on_missing_claim=True,
    verify=True,
    validate_token=True,
    authorization_method=AuthorizationMethod.CLAIM,
    authorization_claim='roles',
    use_introspection_endpoint=False,
    swagger_client_id="web_app",
    swagger_auth_scopes=["openid"],  # Optional
    swagger_auth_pkce=True,  # Optional
    swagger_scheme_name="openid",
    decode_options={
        "verify_signature": True,
        "verify_aud": False,
        "verify_exp": True,
    }
)

app = FastAPI()

# Add middleware with basic config
setup_keycloak_middleware(
    app,
    keycloak_configuration=keycloak_config,
    exclude_patterns=[
        '/management/*',
        '/docs',
        '/openapi.json',
        '/redoc'

    ],
    #user_mapper=map_user,
    add_swagger_auth=True,
)
@app.get("/test")
async def root():
    return {"message": "Hello World"}

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(resources.router)
app.servers = [
    {
        "url": "http://localhost:8000"
    }
]

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://frontend:3000",
    "https://frontend:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/management/health")
async def info():
    return {
        "status": "up"
    }
