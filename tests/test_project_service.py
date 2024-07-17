import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from ina_ground_control.database import Base
from ina_ground_control.services.project_service import create_project_crud, get_projects, get_project_by_id, update_project_crud, delete_project_crud
from ina_ground_control.schemas.project_schemas import ProjectBaseDto
from ina_ground_control.models.project_model import ProjectStatus


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


project_data = {
    "title": "Test Project 1",
    "description": "Test description 2",
    "status": "draft",
    "annotation_type": "segmentation",
    "is_published": True,
    "allow_skip": True,
    "control_weights": 10,
    "empty_annotations": True,
    "pinned_at": "2022-12-27 08:26:49.219717",
    "created_by": "john@example.com",
}


def test_get_projects(db: Session):
    """
        Test to retrieve all the project in the database
    """
    project_data_1 = {
        "title": "Test Project 1",
        "description": "Test description 2",
        "status": "draft",
        "annotation_type": "segmentation",
        "is_published": True,
        "allow_skip": True,
        "control_weights": 10,
        "empty_annotations": True,
        "pinned_at": "2022-12-27 08:26:49.219717",
        "created_by": "john@example.com",
    }
    project_data_2 = {
        "title": "Test Project 2",
        "description": "Test description 2",
        "status": "draft",
        "annotation_type": "segmentation",
        "is_published": True,
        "allow_skip": True,
        "control_weights": 10,
        "empty_annotations": True,
        "pinned_at": "2022-12-27 08:26:49.219717",
        "created_by": "jane@example.com",
    }

    created_project_1 = create_project_crud(
        db, ProjectBaseDto(**project_data_1))
    created_project_2 = create_project_crud(
        db, ProjectBaseDto(**project_data_2))

    retrieved_projects = get_projects(db)

    assert retrieved_projects is not None
    assert retrieved_projects[0].id == created_project_1.id
    assert retrieved_projects[0].description == project_data_1["description"]
    assert retrieved_projects[0].created_by == project_data_1["created_by"]
    assert retrieved_projects[0].title == project_data_1["title"]
    assert retrieved_projects[1].title == project_data_2["title"]
    assert retrieved_projects[1].description == project_data_2["description"]
    assert retrieved_projects[1].created_by == project_data_2["created_by"]
    assert retrieved_projects[1].id == created_project_2.id


def test_get_project_by_id(db: Session):
    """
        Test to get a singualr project given its id.
    """
    created_project = create_project_crud(db, ProjectBaseDto(**project_data))

    retrieved_project = get_project_by_id(db, created_project.id)

    assert retrieved_project is not None
    assert retrieved_project.id == created_project.id
    assert retrieved_project.title == project_data["title"]
    assert retrieved_project.description == project_data["description"]
    assert retrieved_project.created_by == project_data["created_by"]


def test_create_project_crud(db: Session):
    """
        Test the creation of a project
    """
    created_project = create_project_crud(db, ProjectBaseDto(**project_data))

    assert created_project is not None
    assert created_project.id is not None
    assert created_project.title == project_data["title"]
    assert created_project.description == project_data["description"]
    assert created_project.created_by == project_data["created_by"]


def test_update_project_crud(db: Session):
    """
        Test update a project attributes (title, description and author)
    """
    created_project = create_project_crud(db, ProjectBaseDto(**project_data))

    updated_task_data = {
        "title": "Test Project 2",
        "description": "Test description 2",
        "status": "draft",
        "annotation_type": "segmentation",
        "is_published": True,
        "allow_skip": True,
        "control_weights": 10,
        "empty_annotations": True,
        "pinned_at": "2022-12-27 08:26:49.219717",
        "created_by": "jane@example.com",
    }
    update_project_crud(db, ProjectBaseDto(
        **updated_task_data), created_project.id)

    retrieved_updated_project = get_project_by_id(db, created_project.id)

    assert retrieved_updated_project is not None
    assert retrieved_updated_project.title == updated_task_data["title"]
    assert retrieved_updated_project.description == updated_task_data["description"]
    assert retrieved_updated_project.created_by == updated_task_data["created_by"]


def test_delete_project_crud(db: Session):
    """
        Test the deletion of a project given its id
    """
    created_project = create_project_crud(db, ProjectBaseDto(**project_data))

    delete_project_crud(db, created_project.id)

    retrieved_project = get_project_by_id(db, created_project.id)

    assert created_project is not None
    assert retrieved_project is None
