from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload


from src.models.annotation_model import Annotation
from src.schemas.annotation_schemas import AnnotationDto, AnnotationCreate


def create_annotation_crud(db: Session, annotation: AnnotationCreate):
    """
        Allow to create an annotation object an save it in the database.

        Parameters:
        db (Session): Session object which contains connection information, db address etc...
        annotation (AnnotationCreate): Pydantic schemas which contains all information for creating database entry
    """
    anno_db = Annotation(**annotation)
    db.add(anno_db)
    db.commit()
    db.refresh(anno_db)
    return anno_db


def get_annotation_by_task_id_crud(db: Session, task_id: int):
    """
        Return all the anntotation object whose attributes "task_id" matches with the argurment

        Parameters:
        db (Session): Session object which contains connection information, db address etc...
        task_id: Integer that identifies the task which may contains several annotations.
    """
    return db.query(Annotation).filter(Annotation.task_id == task_id).first()
