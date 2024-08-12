from sqlalchemy import Column,Integer, ForeignKey
from ina_ground_control.database import Base


class Media_Project(Base):

    __tablename__="media_project"

    media_id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
