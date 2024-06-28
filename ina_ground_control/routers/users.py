"""
This module defines the API endpoints related to user management within the application.
It includes routes for retrieving user data, utilizing the Keycloak middleware for
authentication and permission checks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.routers.projects import NOT_FOUND_STR
from ina_ground_control.schemas.user_base_schemas import UserBaseDto
from ina_ground_control.schemas.user_schemas import UserDto
from ina_ground_control.services.user_service import (
    create_user_crud,
    get_user_by_email_crud,
    get_users,
)

logger = get_logger()
router = APIRouter(tags=["user"])
NOT_FOUND_STR_USER = "User not found"


@router.get("/users/", response_model=list[UserDto], response_model_by_alias=False)
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


@router.post("/user/", response_model=UserDto, response_model_by_alias=False)
def create_user(user: UserBaseDto, db: Session = Depends(get_db)):
    """
    Create a new User object in database
    """
    try:
        return create_user_crud(db, user)
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=400, detail="Failed to create user")


# FIX: ERROR 500 when the function return the user object
@router.get("/user/")
def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email_crud(db, email)
        if user is not None:
            return status.HTTP_200_OK
    except Exception as e:
        logger.error(f"Failed to retrieve user: {e}")
        raise HTTPException(status_code=404, detail=NOT_FOUND_STR_USER)
