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

import re
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Enum, CheckConstraint, Boolean
from sqlalchemy.orm import validates, relationship

from ina_ground_control.database import Base

class TypePlugin(str, PyEnum):
    """
    Enum representing the different plugin types.

    Values:
        LABEL: Label plugin
        AUTOCOMPLETE: List with autocomplete functionality.
        LIST_ITEMS: Displays tags and list of items.
        SUGGESTION_LIST: Interactive suggestion block.
.       INPUT_LABEL: Simple text input field.
    """
    LABEL = "label"                   # Représente un plugin label
    AUTOCOMPLETE = "autocomplete"     # Présente une liste avec auto-complétion
    LIST_ITEMS = "listitems"           # Affiche des tags et une liste d'éléments
    SUGGESTION_LIST = "suggestionlist" # Bloc de suggestions interactives
    INPUT_LABEL = "inputlabel"         # Affiche un champ de saisie de texte simple

class DisplayZone(str, PyEnum):
    """
    Enum representing the different display zones available for a plugin.

    Attributes:
        BLOC (str): Represents a standalone block zone.
        SPAN_MODAL_LEFT (str): Represents a modal that spans the left side.
        SPAN_MODAL_RIGHT (str): Represents a modal that spans the right side.
        GROUP_MODAL (str): Represents a grouped modal zone for multiple plugins.
    """
    BLOC = "bloc"
    SPAN_MODAL_LEFT = "span_modal_left"
    SPAN_MODAL_RIGHT = "span_modal_right"
    GROUP_MODAL = "group_modal"

class Plugin(Base):
    """
     Represents a plugin configuration record in the database.

     Attributes:
         id (Integer): The unique identifier (Primary Key).
         name (String): The name of the configuration. Must be in lowercase and must not contain spaces.
         type (Enum): The type of plugin configuration.
         step_id (Integer): The foreign key linking to the step table.
         configData (JSON): Additional configuration data.
         display_config (JSON): Additional configuration for display zone .
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
    display_config = Column(JSON, nullable=True)
    enable_search = Column(Boolean, default=False, nullable=True)
    data_property = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("plugin.id"), nullable=True)
    parent = relationship(
        "Plugin",
        back_populates="children",
        remote_side=[id]
    )
    children = relationship(
        "Plugin",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    __table_args__ = (
        CheckConstraint("name = LOWER(name)", name="check_name_lowercase"),
        CheckConstraint("name NOT LIKE '% %'", name="check_name_no_spaces"),
    )

    @validates("configData")
    def validate_config_data(self, value):
        # Validates that the configData JSON contains 'type' as a string and 'datasource' as a valid URL.
        if not isinstance(value, dict):
            raise ValueError("configData must be a JSON object (dictionary).")

        # Check for the required 'type' field
        if "type" not in value or not isinstance(value["type"], str):
            raise ValueError("configData must include a 'type' key with a string value.")

        # Check for the required 'datasource' field
        if "data_source" not in value or not isinstance(value["data_source"], str):
            raise ValueError("configData must include a 'data_source' key with a string value.")

        # Validate 'datasource' as a URL using a regex
        url_pattern = re.compile(
            r"^(https?|ftp)://"
            r"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$"
        )
        if not url_pattern.match(value["data_source"]):
            raise ValueError("The 'data_source' key must contain a valid URL.")

        return value
