"""Unit tests for User services"""

# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

# Import the role/user_role modules so their mappers are registered before the
# User mapper (which relates to UserRole) is configured on first query.
from ina_ground_control.models import (  # noqa: F401  pylint: disable=unused-import
    Base,
    role,
    user_role,
)
from ina_ground_control.models.user_model import User
from ina_ground_control.services.user_service import get_user_by_email_crud


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Mock the database using sqlite
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def db(test_db_engine):
    """
    Create the connection session to interract with sqlite
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


test_user = {
    "email": "test@example.com",
    "firstname": "Test",
    "lastname": "User",
}


def test_get_user_by_email(db: SQLAlchemySession):
    """
    Persist a User and check that it can be retrieved by its email.
    """
    db.add(User(**test_user))
    db.commit()

    retrieved_user = get_user_by_email_crud(db, test_user["email"])

    assert retrieved_user is not None
    assert retrieved_user.email == test_user["email"]
    assert retrieved_user.firstname == test_user["firstname"]
    assert retrieved_user.lastname == test_user["lastname"]


def test_get_user_by_email_not_found(db: SQLAlchemySession):
    """
    Retrieving an unknown email returns None.
    """
    assert get_user_by_email_crud(db, "unknown@example.com") is None
