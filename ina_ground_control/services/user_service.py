"""
Service related to user objects.

Functions:
- get_users
- create_user_crud
- get_user_by_email_crud
"""

from pydantic import EmailStr
from sqlalchemy.orm import Session

from ina_ground_control.models.user_model import User
from ina_ground_control.schemas.user_base_schemas import UserBaseDto


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of users from the database with pagination.

    Parameters:
    db (Session): Session object which contains connection information.
    skip (int): Number of records to skip for pagination.
    limit (int): Maximum number of records to return.

    Returns:
    List[User]: A list of User objects.
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user_crud(db: Session, user: UserBaseDto) -> User:
    """
    Insert the newly created user object in the database.

    Parameters:
    db (Session): Session object which contains connection information.
    user (UserBaseDto): Pydantic schema containing user information.

    Returns:
    User: The newly created User object.
    """
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email_crud(db: Session, email: EmailStr) -> User | None :
    """
    Retrieve a specific user given their email.

    Parameters:
    db (Session): Session object which contains connection information.
    email (EmailStr): The email address of the user to retrieve.

    Returns:
    User: The User object that matches the email or None.
    """
    return db.query(User).filter(User.email == email).first()
