import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.services.plugin_service import get_plugins
from ina_ground_control.schemas.plugin_schemas import PluginCreate,PluginWithIdDto


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
def db_session(db_engine):
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


def test_get_plugins(db_session: Session):
    plugin_1 = {
        "name": "name test",
        "type": "autocomplete",
        "data_categories": "data_categories test",
        "display_zone": "bloc",
        "step_id": "1",
        "configData": {"type": "type test",
                         "datasource": 'test data'}
    }

    plugin_2 = {
        "name": "name test",
        "type": "autocomplete",
        "data_categories": "data_categories test",
        "display_zone": "bloc",
        "step_id": "1",
        "configData": {"type": "type test",
                       "datasource": 'test data'}
    }