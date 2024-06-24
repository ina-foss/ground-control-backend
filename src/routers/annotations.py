"""
   This module configures the routing of all the calls related to
   annotation object.
   It maps each routes with the corresponding service and return the right DTO
   or the error status if something went wrong.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from latios.log import get_logger

from src.database import get_db
from src.models.annotation_model import Annotation
from src.schemas.annotation_schemas import AnnotationDto, AnnotationCreate
from src.services.annotation_service import (
    create_annotation_crud,
    get_annotations_by_task_id_crud,
    get_annotations_by_id_crud,
    udpate_annotation_result_crud,
)

logger = get_logger()
router = APIRouter(tags=["annotation"])


@router.post("/annotation/", response_model=AnnotationDto)
def create_annotation(
        annotation: AnnotationCreate,
        db: Session = Depends(get_db)) -> AnnotationDto:
    """
        Create a new annotation.

        Args:
        annotation (AnnotationCreate): The annotation data

        Returns:
        AnnotationDTO : The newly created annotation
    """
    try:
        return create_annotation_crud(db, annotation)
    except Exception as e:
        logger.error(f"Failed to created annotation: {e}")
        raise HTTPException(
            status_code=400, detail="Failed to create annotation")


@router.get("/annotation/{id}", response_model=AnnotationDto)
def get_annotations_by_id(
        id: int, db: Session = Depends(get_db)) -> AnnotationDto:
    """
        Retrieve a single annotation
    """
    annotation: AnnotationDto = get_annotations_by_id_crud(db, id)
    if annotation is None:
        logger.error(f"Failed to retrieve annotation with id: {id}")
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


@router.get("/annotations/{task_id}", response_model=AnnotationDto)
def get_annotation_by_task_id(
        task_id: int, db: Session = Depends(get_db)) -> list[Annotation]:
    """
        Get a list of annotations that match the task_id attributes
    """
    annotations = get_annotations_by_task_id_crud(db, task_id=task_id)
    return annotations


@router.patch("/annotation/{id}", response_model=AnnotationDto)
def update_annotation_result(
        id: int, result: Dict[str, Any], db: Session = Depends(get_db)) -> AnnotationDto:
    """
        Edit the result of an existing annotation
    """
    annotation = udpate_annotation_result_crud(db, result, id)
    if annotation is None:
        logger.error(f"Failed to retrieve annotation with id: {id}")
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation
