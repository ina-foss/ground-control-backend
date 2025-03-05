"""
This module defines the API endpoints related to tag management within
the application.
Includes routes for creating, retrieving, and updating tagss.
Utilizes database sessions for CRUD operations and handles exceptions
appropriately.

Endpoints:
    /tag/{tag_id}: Retrieves a tag by its ID.
    /tag/: Creates a new tag.
    /tag/{tag_id}: Updates an existing tag by its ID.
    /tag/{tag_id}: Delete tag
    /tags/: Retrieves all tag
Dependencies:
    - External services: None.
    - Internal utilities: Database session, tag service for CRUD operations.

Configuration:
    - Database session configuration and tag schemas are defined in the
    `src` module.
"""

from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from latios.log import get_logger
from ina_ground_control.database import get_db
from ina_ground_control.models.tag_model import Tag
from ina_ground_control.schemas.tag_schemas import TagDto , TagCreate
from ina_ground_control.services.tag_service import get_tag_by_key, create_tag_crud, update_tag_crud,delete_tag_crud,get_tags

logger = get_logger()
router = APIRouter(tags=["tag"])

#get tag by key
@router.get("/tag/{tag_key}", response_model=TagDto)
def read_tag(tag_key: str, db: Session = Depends(get_db)):
    """
    Retrieve a tag by its unique identifier key.

    Args:
        key (str): The unique identifier of the tag.

    Returns:
        TagDto: The requested tag's details.
    Raises:
        HTTPException: If the tag is not found.
    """
    tag = get_tag_by_key(db, tag_key=tag_key)
    if tag is None:
        logger.error("Failed to retrieve tag with id: %d", tag_key)
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

#add new tag
@router.post("/tag", response_model=TagCreate)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """
    Create a new tag.

    Args:
        tag (TagCreate): The tag data to be created.

    Returns:
        TagCreate: The newly created tag's details.
    """
    try:
        unique_tag_key = get_tag_by_key(db, tag_key=tag.key)
        if unique_tag_key is None:
            return create_tag_crud(tag, db)
    except Exception as e:
        logger.error("Failed to create tag: %s", e)
        raise HTTPException(status_code=400, detail="Failed to create tag") from e


#update tag by key
@router.patch("/tag/{tag_key}", response_model=TagDto)
def update_tag(tag_key: str, tag: TagDto, db: Session = Depends(get_db)):
    """
    Update an existing tag by its unique identifier.

    Args:
        tag_key (str): The unique identifier of the tag to update.
        tag (TagDto): The updated tag's value.

    Returns:
        TagDto: The updated tag's details.
    Raises:
        HTTPException: If the tag is not found.
    """
    updated_tag = update_tag_crud(tag_key, tag, db)
    if updated_tag is None:
        logger.error("Failed to update tag with key: %d", tag_key)
        raise HTTPException(status_code=404, detail="tag not found")
    return updated_tag

#delete tag
@router.delete("/tag/{tag_key}", status_code=status.HTTP_200_OK,response_model=TagCreate)
def delete_tag(tag_key: str, db: Session = Depends(get_db)):
    deleted_tag = delete_tag_crud(db, tag_key)
    if deleted_tag is None:
        logger.error("Failed to delete tag with key: %d", tag_key)
        raise HTTPException(status_code=404, detail="Tag not found")
    return deleted_tag

#get list of tag
@router.get("/tags", response_model=list[TagDto])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) \
        -> list[Tag]:
    """Retrieve a list of tags with pagination support."""
    tags = get_tags(db, skip=skip, limit=limit)
    return tags
