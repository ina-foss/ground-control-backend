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
    data_source: Optional[str] = Field(None, alias='data_source')

    # Use ConfigDict for configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra='ignore'
    )
