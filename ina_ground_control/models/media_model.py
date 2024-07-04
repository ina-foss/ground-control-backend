from ina_ground_control.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    url = Column(String,nullable=False)
    projects = relationship("Project", backref="media", cascade="all")
    tasks = relationship("Tasks", backref="media", cascade="all")

