"""
This module provides CRUD operations for tags.

It includes functions to retrieve a tag by ID, create a new tag, and update an existing tag.
"""


from sqlalchemy.orm import Session
from ina_ground_control.models.tag_model import Tag
from ina_ground_control.schemas.tag_schemas import TagCreate,TagDto


def get_tag_by_key(db: Session, tag_key: str):
    """
    Retrieve a tag by its KEY.

    Attributes:
        db (Session): The database session used for querying.
        key (str): The unique identifier of the tag to retrieve.

    Returns:
        Tag: The tag object if found, otherwise None.
    """
    return db.query(Tag).filter(Tag.key == tag_key).first()

def create_tag_crud(tag: TagCreate, db: Session):
    """
    Create a new tag in the database.

    Attributes:
        tag (TagCreate): The tag data transfer object containing tag details.
        db (Session): The database session used for querying.

    Returns:
        Tag: The newly created Tag object.
    """
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def update_tag_crud(tag_key: str, tag: TagDto, db: Session):
    """
    Update the data of an existing tag in the database.

    Attributes:
        tag_key (str): The unique identifier of the tag to update.
        tag (TagCreate): A new url for the tag.
        db (Session): The database session used for querying.

    Returns:
        Tag: The updated Tag object if the tag exists, otherwise None.
    """
    db_tag = get_tag_by_key(db, tag_key)
    if db_tag is not None:
        for key, value in tag.model_dump().items():
            setattr(db_tag, key, value)
        db.commit()
        db.refresh(db_tag)
    return db_tag

def delete_tag_crud(db: Session, tag_key:str):
    """
    Delete a tag from the database.

    Parameters:
    db (Session): The database session used for querying.
    tag_key (str): The unique identifier of the tag to delete.

    Returns:
    Tag: The deleted Tag object if the tag exists, otherwise None.
    """
    db_tag = db.query(Tag).filter(Tag.key == tag_key).first()
    if db_tag is not None:
        db.delete(db_tag)
        db.commit()
    return db_tag

def get_tags(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of tags from the database with optional pagination.

    Parameters:
    db (Session): The database session used for querying.
    skip (int): The number of records to skip for pagination. Default is 0.
    limit (int): The maximum number of records to return. Default is 100.

    Returns:
    List[Tag]: A list of tag objects.
    """
    return db.query(Tag).offset(skip).limit(limit).all()
