"""
This module defines the API endpoints related to user management within the application.
It includes routes for retrieving user data, utilizing the Keycloak middleware for
authentication and permission checks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import EmailStr
from sqlalchemy.orm import Session
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.schemas.user_base_schemas import UserBaseDto
from ina_ground_control.schemas.user_schemas import UserDto
from ina_ground_control.services.user_service import (
    create_user_crud,
    get_user_by_email_crud,
    get_users,
)
from typing import List
from jose import jwt
from ina_ground_control.utils.auth import get_user_info_from_token
from fastapi.security import OAuth2PasswordBearer

logger = get_logger()
router = APIRouter(tags=["user"])
NOT_FOUND_STR_USER = "User not found"

DEFAULT_ROLES = ["default-roles-notilus", "offline_access", "uma_authorization"]

@router.get("/users", response_model=list[UserDto], response_model_by_alias=False)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of users with pagination support.

    Args:
        skip (int): Number of users to skip.
        limit (int): Maximum number of users to retrieve.

    Returns:
        List[UserDto]: A paginated list of user DTOs.
    """
    try:
        users = get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error("Failed to retrieve users: %s", e)
        raise HTTPException(status_code=400, detail="Failed to retrieve users") from e


@router.post("/user", response_model=UserDto, response_model_by_alias=False)
def create_user(user: UserBaseDto, db: Session = Depends(get_db)):
    """
    Create a new User object in database
    """
    try:
        return create_user_crud(db, user)
    except Exception as e:
        logger.error("Failed to create user: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create user") from e


@router.get("/user/")
def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email_crud(db, email)
        if user is not None:
            return status.HTTP_200_OK
    except Exception as e:
        logger.error("Failed to retrieve user: %s", e)
        raise HTTPException(status_code=404, detail=NOT_FOUND_STR_USER) from e

@router.get("/roles", response_model=List[str], response_model_by_alias=False)
def get_roles(authorization: str = Header(...)):
    """
    Retrieve the roles of the current authenticated user and verify if they have basic roles.

    Args:
        authorization (str): Authorization header containing the JWT token.

    Returns:
        List[str]: A list of roles associated with the user, or an error if basic roles are missing.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # Extract the token from the Authorization header
    token = authorization.split("Bearer ")[-1]

    try:
        # Extract roles from the token using the get_user_info_from_token function
        roles = get_user_info_from_token(token)["roles"]

        # Check if the user has the required basic roles
        missing_roles = [role for role in DEFAULT_ROLES if role not in roles]
        if missing_roles:
            raise HTTPException(status_code=403, detail=f"Missing basic roles: {', '.join(missing_roles)}")

        return roles

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode token: {str(e)}")

#@router.get("/admin",dependencies=[Depends(role_required(["ROLE_ADMIN"]))])
#async def admin_dashboard():
#    return {"message": "Bienvenue, administrateur !"}
