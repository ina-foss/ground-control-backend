import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.services.plugin_service import get_plugins,create_plugin_crud
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
        "name": "name_test",
        "type": "autocomplete",
        "data_categories": "data_categories test",
        "display_zone": "bloc",
        "step_id": "1",
        "config_data": {"type": "type test",
                         "datasource": 'test data'}
    }

    plugin_2 = {
        "name": "name_test",
        "type": "autocomplete",
        "data_categories": "data_categories test",
        "display_zone": "bloc",
        "step_id": "1",
        "config_data": {"type": "type test",
                       "datasource": 'test data'}
    }
    created_plugin_1= create_plugin_crud(PluginCreate(**plugin_1), db_session)
    created_plugin_2 = create_plugin_crud(PluginCreate(**plugin_2), db_session)

    retrieved_plugins = get_plugins(db_session)

    assert retrieved_plugins is not None
    assert retrieved_plugins[0].id == created_plugin_1.id
    assert retrieved_plugins[0].name == created_plugin_1["name"]
    assert retrieved_plugins[0].type.value == created_plugin_1["type"]
    assert retrieved_plugins[0].data_categories == created_plugin_1["data_categories"]
    assert retrieved_plugins[0].display_zone.value == created_plugin_1["display_zone"]
    assert retrieved_plugins[0].step_id == created_plugin_1["step_id"]
    assert retrieved_plugins[1].id == created_plugin_2.id
    assert retrieved_plugins[1].name == created_plugin_2["name"]
    assert retrieved_plugins[1].type.value == created_plugin_2["type"]
    assert retrieved_plugins[1].data_categories == created_plugin_2["data_categories"]
    assert retrieved_plugins[1].display_zone.value == created_plugin_2["display_zone"]
    assert retrieved_plugins[1].step_id == created_plugin_2["step_id"]

"""plugin_data = {
    "name": "name test",
    "type": "autocomplete",
    "data_categories": "data_categories test",
    "display_zone": "bloc",
    "step_id": "1",
    "config_data": {"type": "type test",
                   "datasource": 'test data'}
}
def test_create_plugin_crud(db_session: Session):

    created_plugin = create_plugin_crud(PluginCreate(**plugin_data),db_session)
    assert created_plugin is not None
    assert created_plugin.id is not None
    assert created_plugin.name == plugin_data["name"]
    assert created_plugin.type.value == plugin_data["type"]
    assert created_plugin.data_categories == plugin_data["data_categories"]
    assert created_plugin.display_zone.value == plugin_data["display_zone"]
    assert created_plugin.step_id == plugin_data["step_id"]"""
