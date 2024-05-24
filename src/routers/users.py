from fastapi import APIRouter, Depends
from src.database import get_db
from sqlalchemy.orm import Session
from fastapi_keycloak_middleware import require_permission

from src.schemas.user_schemas import UserDto
from src.services.user_service import get_users


router = APIRouter(tags=["user"])

@router.get("/users/", response_model=list[UserDto],response_model_by_alias=False)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users
