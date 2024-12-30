"""
This module defines the API endpoints related to media management within
the application.
Includes routes for creating, retrieving, and updating medias.
Utilizes database sessions for CRUD operations and handles exceptions
appropriately.

Endpoints:
    /media/{media_id}: Retrieves a media by its ID.
    /media/: Creates a new media.
    /media/{media_id}: Updates an existing media by its ID.
    /media/{media_id}: Delete media
    /medias/: Retrieves all media
Dependencies:
    - External services: None.
    - Internal utilities: Database session, media service for CRUD operations.

Configuration:
    - Database session configuration and media schemas are defined in the
    `src` module.
"""

from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.models.media_model import Media
from ina_ground_control.schemas.media_schemas import MediaDto , MediaCreate
from ina_ground_control.services.media_service import get_media_by_id, create_media_crud, update_media_crud,delete_media_crud,get_medias

logger = get_logger()
router = APIRouter(tags=["media"])
MEDIA_NOT_FOUND_MESSAGE = "Media not found"

#get media by id
@router.get("/media/{media_id}", response_model=MediaDto)
def read_media(media_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a media by its unique identifier.

    Args:
        media_id (int): The unique identifier of the media.

    Returns:
        MediaDto: The requested media's details.
    Raises:
        HTTPException: If the media is not found.
    """
    media = get_media_by_id(db, media_id=media_id)
    if media is None:
        logger.error("Failed to retrieve media with id: %d", media_id)
        raise HTTPException(status_code=404, detail=MEDIA_NOT_FOUND_MESSAGE)
    return media

#add new media
@router.post("/media/", response_model=MediaDto)
def create_media(media: MediaCreate, db: Session = Depends(get_db)):
    """
    Create a new media.

    Args:
        media (MediaCreate): The media data to be created.

    Returns:
        MediaCreate: The newly created media's details.
    """
    try:
        return create_media_crud(media, db)
    except Exception as e:
        logger.error("Failed to create media: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create media") from e

#update media by id
@router.patch("/media/{media_id}", response_model=MediaDto)
def update_data_media(media_id: int, media: MediaCreate, db: Session = Depends(get_db)):
    """
    Update an existing media by its unique identifier.

    Args:
        media_id (int): The unique identifier of the media to update.
        data (MediaDto): The updated media data.
s
    Returns:
        MediaDto: The updated media's details.
    Raises:
        HTTPException: If the media is not found.
    """
    media = update_media_crud(media_id, media, db)
    if media is None:
        logger.error("Failed to update media with id: %d", media_id)
        raise HTTPException(status_code=404, detail=MEDIA_NOT_FOUND_MESSAGE)
    return media

#delete media
@router.delete("/media/{media_id}", status_code=status.HTTP_200_OK,response_model=MediaCreate)
def delete_media(media_id: int, db: Session = Depends(get_db)):
    deleted_media = delete_media_crud(db, media_id)
    if deleted_media is None:
        logger.error("Failed to delete media with id: %d", media_id)
        raise HTTPException(status_code=404, detail=MEDIA_NOT_FOUND_MESSAGE)
    return deleted_media

#get list of media
@router.get("/medias/", response_model=list[MediaDto])
def read_medias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) \
        -> list[Media]:
    """Retrieve a list of medias with pagination support."""
    medias = get_medias(db, skip=skip, limit=limit)
    return medias
