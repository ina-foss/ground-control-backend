"""
This module configures the routing of all the calls related to
annotation objects. It maps each route with the corresponding service and returns the right DTO
or the error status if something went wrong.
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ina_ground_control import logger
from ina_ground_control.constants.roles import Role
from ina_ground_control.database import get_db
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.annotation_task_association import InOutEnum
from ina_ground_control.schemas.annotation_schemas import AnnotationDto, AnnotationFullCreate
from ina_ground_control.services.annotation_service import (
    create_annotation_crud,
    get_annotations_by_task_id_crud,
    get_annotations_by_id_crud,
    udpate_annotation_result_crud,
    finish_annotation_crud
)

router = APIRouter(tags=["annotation"])

ERROR_MESSAGE_FAILED_ANNOTATION = "Failed to retrieve annotation with id: %s"
ANNOTATION_NOT_FOUND_MESSAGE = "Annotation not found"


@router.post("/annotation", response_model=AnnotationDto)
def create_annotation(
        annotation: AnnotationFullCreate,
        db: Session = Depends(get_db)) -> AnnotationDto:
    """
    Create a new annotation.

    Args:
    annotation (AnnotationCreate): The annotation data

    Returns:
    AnnotationDTO: The newly created annotation
    """
    try:
        return create_annotation_crud(db, annotation)
    except Exception as e:
        logger.error("Failed to create annotation: %s", e)
        raise HTTPException(
            status_code=400, detail="Failed to create annotation") from e


@router.get("/annotation/{id}", response_model=AnnotationDto)
def get_annotations_by_id(
        annotation_id: int, db: Session = Depends(get_db)) -> AnnotationDto:
    """
    Retrieve a single annotation
    """
    annotation: AnnotationDto = get_annotations_by_id_crud(db, annotation_id)
    if annotation is None:
        logger.error(ERROR_MESSAGE_FAILED_ANNOTATION, annotation_id)
        raise HTTPException(status_code=404, detail=ANNOTATION_NOT_FOUND_MESSAGE)
    return annotation


@router.get("/annotations/{task_id}", response_model=list[AnnotationDto])
def get_annotation_by_task_id(
        task_id: int,
        request: Request,
        user_email: str = Query(None, description="user_email"),
        direction: InOutEnum = Query(None, description="Direction of the annotation ('in' or 'out')"),
        db: Session = Depends(get_db)) -> list[Annotation]:
    """
    Get a list of annotations that match the task_id attributes
        - Admins can retrieve annotations for **any user**.
        - Regular users can only retrieve **their own** annotations.
    """
    user = request.scope.get("user", {})
    email = user.email
    roles = user.roles

    if Role.GC_ADMIN in roles or user_email == "":
        annotations = get_annotations_by_task_id_crud(db, task_id=task_id, direction=direction, user_email=user_email)
    else:
        annotations = get_annotations_by_task_id_crud(db, task_id=task_id, direction=direction, user_email=email)
    return annotations


@router.patch("/annotation/{id}", response_model=AnnotationDto)
def update_annotation_result(
        annotation_id: int, result: Dict[str, Any], db: Session = Depends(get_db)) -> AnnotationDto:
    """
    Edit the result of an existing annotation
    """
    annotation = udpate_annotation_result_crud(db, result, annotation_id)
    if annotation is None:
        logger.error(ERROR_MESSAGE_FAILED_ANNOTATION, annotation_id)
        raise HTTPException(status_code=404, detail=ANNOTATION_NOT_FOUND_MESSAGE)
    return annotation


@router.patch("/annotation/finish/{id}", response_model=AnnotationDto)
def finish_annotation(
        annotation_id: int, result: Dict[str, Any], db: Session = Depends(get_db)) -> AnnotationDto:
    """
    finish an annotation
    """
    annotation = finish_annotation_crud(db, result, annotation_id)
    if annotation is None:
        logger.error(ERROR_MESSAGE_FAILED_ANNOTATION, annotation_id)
        raise HTTPException(status_code=404, detail=ANNOTATION_NOT_FOUND_MESSAGE)
    return annotation
