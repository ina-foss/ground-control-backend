"""
Define the SQLModel models and enums for the plugin management application.

This module includes:
1. The definition of the `Plugin` model, which represents a plugin configuration record in the database.
   It includes attributes such as `name`, `type`, and `configData`, along with constraints to enforce data integrity.

Classes:
    Plugin (SQLModel): SQLModel model representing a plugin configuration record in the database.

Features:
- The `Plugin` model ensures that the `name` field is in lowercase and does not contain
spaces using database-level constraints.
- Additional validation for the `configData` JSON field can be added to ensure it includes
required keys like `type` (string) and `datasource` (valid URL), either in the application logic or as part of database constraints.
"""

# pylint: disable=unsubscriptable-object
import re
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship, validates
from sqlmodel import Field, Relationship, SQLModel

from ina_ground_control.constants.enums import DisplayZone, TypePlugin


class Plugin(SQLModel, table=True):
    """
    Represents a plugin configuration record in the database.

    Attributes:
        id (int): The unique identifier (Primary Key).
        name (str): The name of the configuration. Must be in lowercase and must not contain spaces.
        type (TypePlugin): The type of plugin configuration.
        step_id (int): The foreign key linking to the step table.
        config_data (dict): Additional configuration data.
        display_config (Optional[dict]): Additional configuration for the display zone.
    Table constraints:
        - "check_name_lowercase": Ensures the 'name' field is always in lowercase.
        - "check_name_no_spaces": Ensures the 'name' field does not contain spaces.
    """

    __tablename__ = "plugin"

    id: Optional[int] = Field(default=None, sa_column=Column(Integer, primary_key=True))
    name: str = Field(sa_column=Column(String, nullable=False))
    data_categories: str = Field(sa_column=Column(String, nullable=False))
    type: TypePlugin = Field(sa_column=Column(Enum(TypePlugin), nullable=False))
    display_zone: DisplayZone = Field(
        sa_column=Column(Enum(DisplayZone), nullable=False)
    )
    step_id: int = Field(sa_column=Column(ForeignKey("step.id"), nullable=False))
    available_plugins: Optional[dict] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    config_data: dict = Field(sa_column=Column(JSON, nullable=False))
    display_config: Optional[dict] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    enable_search: Optional[bool] = Field(
        sa_column=Column(Boolean, default=False, nullable=True)
    )
    data_property: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    parent_id: Optional[int] = Field(
        default=None, sa_column=Column(ForeignKey("plugin.id"), nullable=True)
    )

    parent: Optional["Plugin"] = Relationship(
        sa_relationship=relationship(
            "Plugin", back_populates="children", remote_side="Plugin.id"
        )
    )
    children: list["Plugin"] = Relationship(
        sa_relationship=relationship(
            "Plugin",
            back_populates="parent",
            cascade="all, delete-orphan",
            lazy="joined",
        )
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
            raise ValueError(
                "configData must include a 'type' key with a string value."
            )

        # Check for the required 'datasource' field
        if "data_source" not in value or not isinstance(value["data_source"], str):
            raise ValueError(
                "configData must include a 'data_source' key with a string value."
            )

        # Validate 'datasource' as a URL using a regex
        url_pattern = re.compile(
            r"^(https?|ftp)://"
            r"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$"
        )
        if not url_pattern.match(value["data_source"]):
            raise ValueError("The 'data_source' key must contain a valid URL.")

        return value
