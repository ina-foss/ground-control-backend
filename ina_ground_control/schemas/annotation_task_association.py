from pydantic import BaseModel
from ina_ground_control.models.annotation_task_association import InOutEnum

class AnnotationTaskCreate(BaseModel):
    annotation_id: int
    task_id: int
    direction: InOutEnum
