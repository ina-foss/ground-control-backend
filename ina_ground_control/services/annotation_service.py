"""
Service related to annotation objects.

Functions:
- create_annotation_crud
- get_annotations_by_task_id_crud
- get_annotations_by_id_crud
- udpate_annotation_result_crud
- finish_annotation_crud
"""

from typing import Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from ina_ground_control import logger
from ina_ground_control.models.annotation_model import Annotation, AnnotationStatus
from ina_ground_control.models.annotation_task_association import AnnotationTask, InOutEnum
from ina_ground_control.schemas.annotation_schemas import AnnotationFullCreate
from ina_ground_control.exception.exceptions import GroundControlException, ErrorCode

ERROR_MESSAGE_FAILED_ANNOTATION = "Failed to retrieve annotation with id: %s"

def create_annotation_crud(db: Session, data: AnnotationFullCreate):
    """
    Allow to create an annotation object and save it in the database.

    Parameters:
    db (Session): Session object which contains connection information.
    annotation (AnnotationCreate): Pydantic schema which contains all information.

    Returns:
    Annotation: The newly created Annotation object.
    """
    # Take all the attributes of AnnotationCreate schemas
    # to create a sqlalchemy model
    anno_db = Annotation(**data.annotation.model_dump())
    db.add(anno_db)
    db.flush()
    association_data = data.association.model_dump()
    association_data["annotation_id"] = anno_db.id
    association_db = AnnotationTask(**association_data)
    db.add(association_db)
    db.commit()
    db.refresh(anno_db)
    return anno_db


def get_annotations_by_id_crud(db: Session, annotation_id: int):
    """
    Retrieve the annotation corresponding to the annotation_id parameter.

    Parameters:
    db (Session): Session object which contains connection information.
    annotation_id (int): Integer that corresponds to the annotation ID.

    Returns:
    Annotation: The Annotation model that matches the id or None.
    """
    annotation =  db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if annotation is None:
        logger.error(ERROR_MESSAGE_FAILED_ANNOTATION, annotation_id)
        raise GroundControlException(ErrorCode.RESOURCE_NOT_FOUND, resource="Annotation", id=annotation_id)
    return annotation


def get_annotations_by_task_id_crud(db: Session,
                                    task_id: int,
                                    user_email: str | None,
                                    direction: InOutEnum,
                                    status: AnnotationStatus | list[AnnotationStatus] | None = None
                                    ) -> list[Annotation]:
    """
    Return all the annotation objects whose attribute "task_id" matches the argument.

    Parameters:
    db (Session): Session object which contains connection information.
    task_id (int): Integer that identifies the task which may contain several annotations.

    Returns:
    List[Annotation]: A list of Annotation objects that match the task_id.
    """

    query = db.query(Annotation).join(
        AnnotationTask, Annotation.id == AnnotationTask.annotation_id
    ).filter(
        AnnotationTask.task_id == task_id,
        AnnotationTask.direction == direction
    )

    if user_email is not None and user_email != "":
        query = query.filter(Annotation.user_email == user_email)
    if status is not None :
        if isinstance(status,list):
            for anno_status in status:
                query = query.filter(Annotation.annotation_status == anno_status)
                pass
        else:
            query = query.filter(Annotation.annotation_status == status)

    return query.all()


def udpate_annotation_result_crud(db: Session, result: Dict[str, Any], annotation_id: int) -> Annotation:
    """
    Edit the attribute "result" of the annotation object that matches the ID.

    Parameters:
    db (Session): Session object which contains connection information.
    result (Dict[str, Any]): JSON object containing the original task data + the segmentation information.
    annotation_id (int): Integer that corresponds to the annotation ID.

    Return:
    Annotation: The updated Annotation object.
    """
    db_annotation = get_annotations_by_id_crud(db, annotation_id)
    db_annotation.result = result
    db.commit()
    db.refresh(db_annotation)
    return db_annotation

def skip_annotation_crud(db:Session, annotation_id: int ) -> Annotation :
    """
    If the project configuration authorize it, change the status of the annotation obejct to `skipped`

    Parameters:
    db (Session): Session object which contains connection information.
    annotation_id (int): Integer that corresponds to the annotation ID.

    Return:
    Annotation: The updated Annotation object.
    """
    db_annotation = get_annotations_by_id_crud(db, annotation_id)
    # Check if the project authorize the skipped state
    if db_annotation.task[0].step.project.allow_skip is False:
        logger.error("Failed to skip annotation with id: %d", annotation_id)
        raise GroundControlException(ErrorCode.GENERIC_CLIENT_ERROR,
              details = "Skipping annotation is not allowed because 'allow_skip' is set to False in the project configuration")
    db_annotation.annotation_status = AnnotationStatus.SKIPPED
    db_annotation.updated_at = func.now()
    db.commit()
    db.refresh(db_annotation)
    return  db_annotation


def finish_annotation_crud(db: Session, result: Dict[str, Any], annotation_id: int) -> Annotation:
    db_annotation = get_annotations_by_id_crud(db, annotation_id)
    db_annotation.result = result
    db_annotation.annotation_status = AnnotationStatus.DONE
    db_annotation.validated_at = func.now()
    db_annotation.updated_at = func.now()
    db.commit()
    db.refresh(db_annotation)
    return db_annotation
