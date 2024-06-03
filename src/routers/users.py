"""
This module defines the API endpoints related to user management within the application.
It includes routes for retrieving user data, utilizing the Keycloak middleware for
authentication and permission checks.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from latios.log import get_logger
from src.database import get_db
from src.schemas.user_schemas import UserDto
from src.services.user_service import get_users

logger = get_logger()
router = APIRouter(tags=["user"])


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
        logger.error(f"Failed to retrieve users: {e}")
        raise HTTPException(status_code=400, detail="Failed to retrieve users")
