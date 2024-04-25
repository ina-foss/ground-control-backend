from fastapi import APIRouter, Depends
from database import get_db
from sqlalchemy.orm import Session


from schemas.user_schemas import User
from crud.users import get_users


router = APIRouter(tags=["user"])

@router.get("/users/", response_model=list[User],response_model_by_alias=False)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users