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
required keys like `type` (string) and `datasource` (valid URL), either in the application logic or as part of database constraints.
"""

# pylint: disable=unsubscriptable-object
import re

from sqlalchemy import JSON, Boolean, CheckConstraint, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ina_ground_control.constants.enums import DisplayZone, TypePlugin
from ina_ground_control.models import Base


class Plugin(Base):
    """
    Represents a plugin configuration record in the database.

    Attributes:
        id (Mapped[int]): The unique identifier (Primary Key).
        name (Mapped[str]): The name of the configuration. Must be in lowercase and must not contain spaces.
        type (Mapped[TypePlugin]): The type of plugin configuration.
        step_id (Mapped[int]): The foreign key linking to the step table.
        config_data (Mapped[dict]): Additional configuration data.
        display_config (Mapped[dict | None]): Additional configuration for the display zone.
    Table constraints:
        - "check_name_lowercase": Ensures the 'name' field is always in lowercase.
        - "check_name_no_spaces": Ensures the 'name' field does not contain spaces.
    """

    __tablename__ = "plugin"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    data_categories: Mapped[str] = mapped_column(String)
    type: Mapped[TypePlugin] = mapped_column(Enum(TypePlugin))
    display_zone: Mapped[DisplayZone] = mapped_column(Enum(DisplayZone))
    step_id: Mapped[int] = mapped_column(ForeignKey("step.id"))
    available_plugins: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    config_data: Mapped[dict] = mapped_column(JSON)
    display_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enable_search: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    data_property: Mapped[str | None] = mapped_column(String, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("plugin.id"), nullable=True
    )

    parent: Mapped["Plugin"] = relationship(
        "Plugin", back_populates="children", remote_side="Plugin.id"
    )
    children: Mapped[list["Plugin"]] = relationship(
        "Plugin", back_populates="parent", cascade="all, delete-orphan", lazy="joined"
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
