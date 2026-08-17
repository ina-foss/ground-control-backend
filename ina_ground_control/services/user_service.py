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


def get_user_by_email_crud(db: Session, email: EmailStr) -> User | None:
    """
    Retrieve a specific user given their email.

    Parameters:
    db (Session): Session object which contains connection information.
    email (EmailStr): The email address of the user to retrieve.

    Returns:
    User: The User object that matches the email or None.
    """
    return db.query(User).filter(User.email == email).first()
