"""
This module defines the base and specific configuration models for plugins.

The `PluginConfigBase` class serves as the foundational configuration for plugins,
enforcing model validation rules and managing optional data sources. Derived from
Pydantic's `BaseModel`, it adds flexibility and robust data handling for plugin setups.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PluginConfigType(str, Enum):
    POST_PLUGIN = "post plugin"
    GET_PLUGIN = "get plugin"
    WIKIDATA = "wikidata"


class DataTypeEnum(str, Enum):
    JSON = "json"


class PluginConfigBase(BaseModel):
    """
    Base configuration for plugins, specifying how data should be retrieved and handled.

    Attributes:
        type (PluginConfigType): Indicates whether the plugin uses POST-based or GET-based search.
        data_type (DataTypeEnum, optional): Type of expected response data. Only 'json' is currently supported.
        data_source (str, optional): The URL or reference of the data source.
    """

    type: PluginConfigType
    data_type: Optional[DataTypeEnum] = Field(None, alias="data_type")
    data_source: Optional[str] = Field(None, alias="data_source")
    # Auth fields
    token_url: Optional[str] = Field(None, alias="token_url")
    client_id: Optional[str] = Field(None, alias="client_id")
    client_secret: Optional[str] = Field(None, alias="client_secret")
    # Use ConfigDict for configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True, populate_by_name=True, extra="allow"
    )
