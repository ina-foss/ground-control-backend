"""
This module defines the base and specific configuration models for plugins.

The `PluginConfigBase` class serves as the foundational configuration for plugins,
enforcing model validation rules and managing optional data sources. Derived from
Pydantic's `BaseModel`, it adds flexibility and robust data handling for plugin setups.
"""


from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PluginConfigBase(BaseModel):
    """
    This class serves as the base configuration for plugins, providing mechanisms
    for managing plugin-specific data sources and enforcing model configuration
    rules.

    :ivar type: The type of the plugin configuration.
    :type type: str
    :ivar data_source: The optional data source associated with the plugin. This
        allows plugins to specify a source of data that may be used during their
        operations.
    :type data_source: Optional[str]
    """
    type: str
    data_type: Optional[str] = Field(None, alias='data_type')
    data_source: Optional[str] = Field(None, alias='data_source')

    # Use ConfigDict for configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra='allow'
    )
