"""
This module defines the API endpoints related to user management within the application.
It includes routes for retrieving user data, utilizing the Keycloak middleware for
authentication and permission checks.
"""

from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from ina_ground_control import get_db, logger
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.services.user_service import get_user_by_email_crud

router = APIRouter(tags=["user"])


@router.get("/user/")
def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email_crud(db, email)
        if user is not None:
            return status.HTTP_200_OK
    except Exception as e:
        logger.error("Failed to retrieve user: %s", e)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="User", id=email
        ) from e


@router.get("/user/roles", response_model=Permission)
def get_all_roles():
    roles = Permission.CREATE_TASK_COMMENT
    return roles
