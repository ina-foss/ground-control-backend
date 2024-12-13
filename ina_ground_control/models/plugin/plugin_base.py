from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field



class PluginConfigBase(BaseModel):
    type: str
    data_source: Optional[str] = Field(None, alias="data_source")

    # Use ConfigDict for configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra='ignore'
    )