"""Unit tests for User services"""
# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.schemas.user_base_schemas import UserBaseDto
from ina_ground_control.services.user_service import create_user_crud, get_user_by_email_crud,get_users


@pytest.fixture(scope="session")
def test_db_engine():
    """
        Mock the databalse using sqlite
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
    "role": "admin",
}


def test_create_user_crud(db: SQLAlchemySession):
    """
    Create a User object and check if it corresponds to the initial data
    """

    created_user = create_user_crud(db, UserBaseDto(**test_user))

    assert created_user.email == test_user["email"]
    assert created_user.role == test_user["role"]


def test_get_user_by_email(db: SQLAlchemySession):
    """
    Retrieve the User object created before and check if it corresponds to the initial data
    """

    retrieved_user = get_user_by_email_crud(db, test_user["email"])

    assert retrieved_user.email == test_user["email"]
    assert retrieved_user.role == test_user["role"]

def test_get_users(db: SQLAlchemySession):
    """
    Retrieve the User object created before and check if it corresponds to the initial data
    """

    retrieved_users = get_users(db,skip=0, limit=10)
    assert len(retrieved_users) == 1
    assert retrieved_users[0].email == test_user["email"]
    assert retrieved_users[0].role == test_user["role"]
