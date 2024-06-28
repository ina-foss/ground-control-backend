from pydantic import EmailStr
from sqlalchemy.orm import Session
from ina_ground_control.models.user_model import User
from ina_ground_control.schemas.user_base_schemas import UserBaseDto


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user_crud(db: Session, user: UserBaseDto) -> User:
    """ "
    Service to insert the newly created user object in the database
    """
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email_crud(db: Session, email: EmailStr) -> User:
    """ "
    Service to retrieve a specific user given its email
    """
    return db.query(User).filter(User.email == email).first()
