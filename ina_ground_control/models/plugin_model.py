"""
Define the SQLAlchemy models and enums for the plugin management application.

This module includes:
1. The definition of the `Plugin` model, which represents a plugin configuration record in the database.
   It includes attributes such as `name`, `type`, and `configData`, along with constraints to enforce data integrity.
2. The `TypePlugin` enum, which defines the available plugin types (e.g., `LABEL`, `AUTOCOMPLETE`).

Classes:
    TypePlugin (PyEnum): Enum representing the different types of plugins available.
    Plugin (Base): SQLAlchemy model representing a plugin configuration record in the database.

Features:
- The `Plugin` model ensures that the `name` field is in lowercase and does not contain
spaces using database-level constraints.
- Additional validation for the `configData` JSON field can be added to ensure it includes
 required keys like `type` (string) and
  `datasource` (valid URL), either in the application logic or as part of database constraints.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum, CheckConstraint
from sqlalchemy.sql.expression import func
from ina_ground_control.database import Base
from enum import Enum as PyEnum
from sqlalchemy.orm import validates
import re

class TypePlugin(PyEnum):
    """
      Enum representing the different types available for plugin.

      Attributes:
          LABEL (str): Represents a label plugin.
          AUTOCOMPLETE (str): Represents an autocomplete plugin.
      """
    LABEL = "label"
    AUTOCOMPLETE = "autocomplete"

class DisplayZone(PyEnum):
    """
  Enum representing the different display zone available for plugin.

      Attributes:
          BLOC (str): Represents a bloc zone.
          COMPONENT (str): Represents a component zone.
    """
    BLOC = "bloc"
    COMPONENT = "component"

class Plugin(Base):
    """
     Represents a plugin configuration record in the database.

     Attributes:
         id (Integer): The unique identifier (Primary Key).
         name (String): The name of the configuration. Must be in lowercase and must not contain spaces.
         type (Enum): The type of plugin configuration.
         step_id (Integer): The foreign key linking to the step table.
         configData (JSON): Additional configuration data.

     Table constraints:
         - "check_name_lowercase": Ensures the 'name' field is always in lowercase.
         - "check_name_no_spaces": Ensures the 'name' field does not contain spaces.
     """

    __tablename__ = "plugin"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    data_categories = Column(String)
    type = Column(Enum(TypePlugin))
    display_zone = Column(Enum(DisplayZone))
    step_id = Column(Integer, ForeignKey("step.id"))
    config_data = Column(JSON)

    __table_args__ = (
        CheckConstraint("name = LOWER(name)", name="check_name_lowercase"),
        CheckConstraint("name NOT LIKE '% %'", name="check_name_no_spaces"),
    )

    @validates("configData")
    def validate_config_data(self, key, value):
        #Validates that the configData JSON contains 'type' as a string and 'datasource' as a valid URL.
        if not isinstance(value, dict):
            raise ValueError("configData must be a JSON object (dictionary).")

        # Check for the required 'type' field
        if "type" not in value or not isinstance(value["type"], str):
            raise ValueError("configData must include a 'type' key with a string value.")

        # Check for the required 'datasource' field
        if "datasource" not in value or not isinstance(value["datasource"], str):
            raise ValueError("configData must include a 'datasource' key with a string value.")

        # Validate 'datasource' as a URL using a regex
        url_pattern = re.compile(
            r'^(https?|ftp)://'
            r'(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$'
        )
        if not url_pattern.match(value["datasource"]):
            raise ValueError("The 'datasource' key must contain a valid URL.")

        return value
