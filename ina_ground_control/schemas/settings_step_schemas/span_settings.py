"""Pydantic models defining the settings of a SPAN step."""

from pydantic import BaseModel, ConfigDict, Field

from ina_ground_control.constants.enums import SpanMode
from ina_ground_control.schemas.settings_step_schemas.common_settings import (
    DisplayableStepSettings,
)
from ina_ground_control.schemas.settings_step_schemas.step_settings_enum import (
    SpanAction,
)


class Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_enabled: bool = True
    id: str


class SpanMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amalia_transcription: Metadata = Field(
        default_factory=lambda: Metadata(id="amalia-transcription")
    )
    transcription: Metadata = Field(
        default_factory=lambda: Metadata(id="summary-transcription")
    )


class SpanSettings(DisplayableStepSettings):
    mode: SpanMode = SpanMode.MONO
    metadata: SpanMetadata = Field(default_factory=SpanMetadata)
    actions: list[SpanAction] = Field(
        default=[
            SpanAction.ADD,
            SpanAction.EDIT_PROPERTIES,
            SpanAction.EDIT_EDGES,
            SpanAction.REMOVE,
        ]
    )
