from ina_ground_control.database import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class Tag(Base):
    __tablename__ = "tag"

    key = Column(String, primary_key=True)
    value = Column(String)
    projects = relationship("Project", backref="tag", cascade="all")


