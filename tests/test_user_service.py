# TODO: Write test for creating user
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.schemas.user_base_schemas import UserBaseDto
from ina_ground_control.services.user_service import create_user_crud, get_user_by_email_crud


@pytest.fixture(scope="session")
def db_engine():
    """
        Mock the databalse using sqlite
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def db(db_engine):
    """
        Create the connection session to interract with sqlite
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


test_user = {
    "email": "test@example.com",
    "role": "admin",
}


def test_create_user_crud(db: Session):
    """
    Create a User object and check if it corresponds to the initial data
    """

    created_user = create_user_crud(db, UserBaseDto(**test_user))

    assert created_user.email == test_user['email']
    assert created_user.role == test_user["role"]

def test_get_user_by_email(db: Session):
    """
    Retrieve the User object created before and check if it corresponds to the initial data
    """

    retrieved_user = get_user_by_email_crud(db,test_user["email"]) 
    
    assert retrieved_user.email == test_user["email"]
    assert retrieved_user.role == test_user["role"]
