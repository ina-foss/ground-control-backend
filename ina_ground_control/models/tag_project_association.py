from sqlalchemy import Column,Integer, ForeignKey, String
from ina_ground_control.database import Base


class Tag_Project(Base):

    __tablename__="tag_project"

    tag_key = Column(String, ForeignKey("tag.key"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
