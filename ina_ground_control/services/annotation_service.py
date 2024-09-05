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
from ina_ground_control.models.annotation_model import Annotation
from ina_ground_control.models.annotation_task_association import Annotation_Task
from ina_ground_control.models.annotation_task_association import Annotation_Task, InOutEnum
from ina_ground_control.schemas.annotation_schemas import AnnotationCreate,AnnotationFullCreate

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
    anno_db= Annotation(**data.annotation.model_dump())
    db.add(anno_db)
    db.flush()
    association_data = data.association.model_dump()
    association_data['annotation_id'] = anno_db.id
    association_db = Annotation_Task(**association_data)
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
    return db.query(Annotation).filter(Annotation.id == annotation_id).first()



def get_annotations_by_task_id_crud(db: Session, task_id: int, direction: InOutEnum):
    """
    Return all the annotation objects whose attribute "task_id" matches the argument.

    Parameters:
    db (Session): Session object which contains connection information.
    task_id (int): Integer that identifies the task which may contain several annotations.

    Returns:
    List[Annotation]: A list of Annotation objects that match the task_id.
    """
    return db.query(Annotation).join(Annotation_Task).filter(
        Annotation.id == Annotation_Task.annotation_id,
        Annotation_Task.task_id == task_id,
        Annotation_Task.direction == direction
    ).all()


def udpate_annotation_result_crud(db: Session, result: Dict[str, Any], annotation_id: int) -> Annotation:
    """
    Edit the attribute "result" of the annotation object that matches the ID.

    Parameters:
    db (Session): Session object which contains connection information.
    result (Dict[str, Any]): JSON object containing the original task data + the segmentation information.
    annotation_id (int): Integer that corresponds to the annotation ID.

    Returns:
    Annotation: The updated Annotation object.
    """
    db_annotation = get_annotations_by_id_crud(db, annotation_id)
    if db_annotation is not None:
        db_annotation.result = result
        db.commit()
        db.refresh(db_annotation)
    return db_annotation

def finish_annotation_crud(db: Session, result: Dict[str, Any], annotation_id: int) -> Annotation:

    db_annotation = get_annotations_by_id_crud(db, annotation_id)
    if db_annotation is not None:
        db_annotation.result = result
        db_annotation.annotation_status = AnnotationStatus.ENDED
        db_annotation.validated_at =func.now()
        db_annotation.updated_at =func.now()
        db.commit()
        db.refresh(db_annotation)
    return db_annotation