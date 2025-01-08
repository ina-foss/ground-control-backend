import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.services.plugin_service import get_plugins_search,create_plugin_crud,get_plugins_crud,delete_plugin_crud,get_plugin_by_id
from ina_ground_control.schemas.plugin_schemas import PluginCreate,PluginWithIdDto
from ina_ground_control.models.plugin_model import TypePlugin,DisplayZone

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
        "type":TypePlugin.AUTOCOMPLETE,
        "data_categories": "data_categories test",
        "display_zone": DisplayZone.BLOC,
        "step_id": 1,
        "config_data": {
            "type": "plugin_autocomplete",
            "data_type": "json",
            "data_source": "https://player-expert.d.sas.ina/assets/listOfChannel/tvChannels.json",
            "search_attr": "title",
            "response_id_key": "$[*].id",
            "response_ext_id_key": "$[*].code",
            "response_label_key": "$[*].label"
        }
    }


    plugin_2 = {
        "name": "name_test2",
        "type": TypePlugin.AUTOCOMPLETE,
        "data_categories": "data_categories test",
        "display_zone": DisplayZone.BLOC,
        "step_id": 2,
        "config_data": {
            "type": "plugin_autocomplete",
            "data_type": "json",
            "data_source": "https://ground-control.2ia.d.sas.ina/cptall-fr.json",
            "search_attr": "title",
            "response_id_key": "$.conceptSet[*].qcode",
            "response_ext_id_key": "$.conceptSet[*].uri",
            "response_label_key": "$.conceptSet[*].prefLabel.fr"
        }
    }
    created_plugin_1= create_plugin_crud(PluginCreate(**plugin_1), db_session)
    created_plugin_2 = create_plugin_crud(PluginCreate(**plugin_2), db_session)
    assert created_plugin_1 is not None
    assert created_plugin_2 is not None
    db_session.commit()
    db_session.refresh(created_plugin_1)
    db_session.refresh(created_plugin_2)
    givenPlugin= get_plugin_by_id(db_session,1)
    assert givenPlugin is not None
    assert givenPlugin.id is not None
    assert givenPlugin.id == 1
    givenPlugin2= get_plugin_by_id(db_session,2)
    assert givenPlugin2 is not None
    assert givenPlugin2.id is not None
    assert givenPlugin2.id == 2
    retrieved_plugins = get_plugins_search(db_session, 1, "name_test")
    retrieved_plugins2 = get_plugins_search(db_session, 2, "name_test2")
    assert retrieved_plugins is not None
    assert retrieved_plugins[0].id is not None
    assert retrieved_plugins[0].id == 'ALAMAIS'
    assert retrieved_plugins[0].ext_id=='ALA'
    assert retrieved_plugins[0].label == '#Alamaison'
    assert retrieved_plugins2 is not None
    assert retrieved_plugins2[0].id is not None
    assert retrieved_plugins2[0].id == 'medtop:01000000'
    assert retrieved_plugins2[0].ext_id=='http://cv.iptc.org/newscodes/mediatopic/01000000'
    assert retrieved_plugins2[0].label == 'Arts, culture, divertissement et médias'

plugin_data = {
    "name": "name_test",
    "type": TypePlugin.AUTOCOMPLETE,
    "data_categories": "data_categories test",
    "display_zone":DisplayZone.BLOC,
    "step_id": 1,
    "config_data": {"type": "plugin_autocomplete",
                    "data_source": 'test data',
                    "data_type": "test"}
}
def test_create_plugin_crud(db_session: Session):

    created_plugin = create_plugin_crud(PluginCreate(**plugin_data),db_session)
    assert created_plugin is not None
    assert created_plugin.id is not None
    assert created_plugin.name == plugin_data["name"]
    assert created_plugin.type == plugin_data["type"]
    assert created_plugin.data_categories == plugin_data["data_categories"]
    assert created_plugin.display_zone == plugin_data["display_zone"]
    assert created_plugin.step_id == plugin_data["step_id"]

def test_delete_plugin_crud(db_session: Session):
    """
        Test the deletion of a plugin given its id
    """
    plugin_1 = {
        "name": "name_test",
        "type": TypePlugin.AUTOCOMPLETE,
        "data_categories": "data_categories test",
        "display_zone": DisplayZone.BLOC,
        "step_id": 1,
        "config_data": {"type": "plugin_autocomplete",
                        "data_source": 'test data',
                        "data_type": "test"}
    }
    created_plugin= create_plugin_crud(PluginCreate(**plugin_1), db_session)

    delete_plugin_crud(db_session, created_plugin.id)

    retrieved_plugin = get_plugin_by_id(db_session, created_plugin.id)

    assert created_plugin is not None
    assert retrieved_plugin is None
