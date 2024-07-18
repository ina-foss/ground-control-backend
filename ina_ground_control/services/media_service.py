"""
This module provides CRUD operations for medias.

It includes functions to retrieve a media by ID, create a new media, and update an existing media.
"""


from sqlalchemy.orm import Session
from ina_ground_control.models.media_model import Media
from ina_ground_control.schemas.media_schemas import MediaCreate


def get_media_by_id(db: Session, media_id: int):
    """
    Retrieve a media by its ID.

    Attributes:
        db (Session): The database session used for querying.
        media_id (int): The unique identifier of the media to retrieve.

    Returns:
        Media: The media object if found, otherwise None.
    """
    return db.query(Media).filter(Media.id == media_id).first()

def create_media_crud(media: MediaCreate, db: Session):
    """
    Create a new media in the database.

    Attributes:
        media (MediaCreate): The media data transfer object containing media details.
        db (Session): The database session used for querying.

    Returns:
        Media: The newly created Media object.
    """
    db_media = Media(**media.model_dump())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def update_data_media_crud(media_id: int, data: str, db: Session):
    """
    Update the data of an existing media in the database.

    Attributes:
        media_id (int): The unique identifier of the media to update.
        data (str): A new url for the media.
        db (Session): The database session used for querying.

    Returns:
        Media: The updated Media object if the media exists, otherwise None.
    """
    db_media = get_media_by_id(db, media_id=media_id)
    if db_media is not None:
        db_media.url = data
        db.commit()
        db.refresh(db_media)
    return db_media

def delete_media_crud(db: Session, media_id: int):
    """
    Delete a media from the database.

    Parameters:
    db (Session): The database session used for querying.
    media_id (int): The unique identifier of the media to delete.

    Returns:
    Media: The deleted Media object if the media exists, otherwise None.
    """
    db_media = db.query(Media).filter(Media.id == media_id).first()
    if db_media is not None:
        db.delete(db_media)
        db.commit()
    return db_media

def get_medias(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of medias from the database with optional pagination.

    Parameters:
    db (Session): The database session used for querying.
    skip (int): The number of records to skip for pagination. Default is 0.
    limit (int): The maximum number of records to return. Default is 100.

    Returns:
    List[Media]: A list of media objects.
    """
    return db.query(Media).offset(skip).limit(limit).all()