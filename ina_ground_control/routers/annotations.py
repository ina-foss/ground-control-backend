"""
This module configures the routing of all the calls related to
annotation objects. It maps each route with the corresponding service and returns the right DTO
or the error status if something went wrong.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from ina_ground_control import get_db, logger
from ina_ground_control.constants.roles import Permission
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException
from ina_ground_control.models.annotation_model import Annotation, AnnotationStatus
from ina_ground_control.models.annotation_task_association import InOutEnum
from ina_ground_control.schemas.annotation_schemas import (
    AnnotationDto,
    AnnotationFullCreate,
)
from ina_ground_control.services.annotation_service import (
    create_annotation_crud,
    finish_annotation_crud,
    get_all_annotations_crud,
    get_annotations_by_id_crud,
    get_annotations_by_task_id_crud,
    skip_annotation_crud,
    udpate_annotation_result_crud,
)
from ina_ground_control.services.task_service import recalculate_task_status

router = APIRouter(tags=["annotation"])

ERROR_MESSAGE_FAILED_ANNOTATION = "Failed to retrieve annotation with id: %s"
ANNOTATION_NOT_FOUND_MESSAGE = "Annotation not found"


@router.post("/annotation", response_model=AnnotationDto)
def create_annotation(
    annotation: AnnotationFullCreate, db: Session = Depends(get_db)
) -> AnnotationDto:
    """
    Create a new annotation.

    Args:
    annotation (AnnotationCreate): The annotation data

    Returns:
    AnnotationDTO: The newly created annotation
    """
    try:
        created_annotation = create_annotation_crud(db, annotation)
        if created_annotation.task:
            recalculate_task_status(db, created_annotation.task[0].id)
        return created_annotation
    except Exception as e:
        logger.error("Failed to create annotation: %s", e)
        raise GroundControlException(
            ErrorCode.GENERIC_CLIENT_ERROR, details="Failed to create annotation"
        ) from e


@router.get("/annotation/{annotation_id}", response_model=AnnotationDto)
def get_annotations_by_id(
    annotation_id: int, db: Session = Depends(get_db)
) -> AnnotationDto:
    """
    Retrieve a single annotation
    """
    annotation: AnnotationDto = get_annotations_by_id_crud(db, annotation_id)
    return annotation


@router.get("/annotations/{task_id}", response_model=list[AnnotationDto])
def get_annotation_by_task_id(
    task_id: int,
    request: Request,
    user_email: str = Query(None, description="user_email"),
    direction: InOutEnum = Query(
        None, description="Direction of the annotation ('in' or 'out')"
    ),
    db: Session = Depends(get_db),
) -> list[Annotation]:
    """
    Get a list of annotations that match the task_id attributes
        - Admins can retrieve annotations for **any user**.
        - Regular users can only retrieve **their own** annotations.
    """
    user = request.scope.get("user", {})
    email = user.email
    roles = user.roles

    if Permission.REVIEW_ANNOTATION.value in roles or user_email == "":
        annotations = get_annotations_by_task_id_crud(
            db, task_id=task_id, direction=direction, user_email=user_email
        )
    else:
        annotations = get_annotations_by_task_id_crud(
            db, task_id=task_id, direction=direction, user_email=email
        )
    return annotations


@router.patch("/annotation/{annotation_id}", response_model=AnnotationDto)
def update_annotation_result(
    annotation_id: int, result: Dict[str, Any], db: Session = Depends(get_db)
) -> AnnotationDto:
    """
    Edit the result of an existing annotation
    """
    annotation = udpate_annotation_result_crud(db, result, annotation_id)
    if annotation is None:
        logger.error(ERROR_MESSAGE_FAILED_ANNOTATION, annotation_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Annotation", id=annotation_id
        )
    return annotation


@router.patch("/annotation/skip/{annotation_id}", response_model=AnnotationDto)
def skip_annotation(annotation_id: int, db: Session = Depends(get_db)) -> AnnotationDto:
    """
    skip an annotation
    """
    annotation = skip_annotation_crud(db, annotation_id)
    recalculate_task_status(db, annotation.task[0].id)
    return annotation


@router.patch("/annotation/finish/{annotation_id}", response_model=AnnotationDto)
def finish_annotation(
    annotation_id: int, result: Dict[str, Any], db: Session = Depends(get_db)
) -> AnnotationDto:
    """
    finish an annotation
    """
    annotation = finish_annotation_crud(db, result, annotation_id)
    recalculate_task_status(db, annotation.task[0].id)
    if annotation is None:
        logger.error(ERROR_MESSAGE_FAILED_ANNOTATION, annotation_id)
        raise GroundControlException(
            ErrorCode.RESOURCE_NOT_FOUND, resource="Annotation", id=annotation_id
        )
    return annotation


@router.get("/annotations", response_model=list[AnnotationDto])
def get_all_annotations(
    user_email: str = Query(None, description="user_email"),
    status: AnnotationStatus = Query(None, description="annotation_status"),
    project_id: int = Query(None, description="project id"),
    step_id: int = Query(None, description="step id"),
    start_created_at: datetime = Query(None, description="start create date"),
    end_created_at: datetime = Query(None, description="end create date"),
    start_updated_at: datetime = Query(None, description="start update date"),
    end_updated_at: datetime = Query(None, description="end update date"),
    start_validated_at: datetime = Query(None, description="start validation date"),
    end_validated_at: datetime = Query(None, description="end validation date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[Annotation]:
    """Get a list of annotations that match the search params"""
    annotations = get_all_annotations_crud(
        db,
        user_email=user_email,
        status=status,
        project_id=project_id,
        step_id=step_id,
        start_created_at=start_created_at,
        end_created_at=end_created_at,
        start_updated_at=start_updated_at,
        end_updated_at=end_updated_at,
        start_validated_at=start_validated_at,
        end_validated_at=end_validated_at,
        skip=skip,
        limit=limit,
    )
    return annotations
