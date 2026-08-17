"""Pydantic model defining the settings of a TRANSCRIPTION step."""

from ina_ground_control.schemas.settings_step_schemas.common_settings import (
    BaseStepSettings,
)


class TranscriptionSettings(BaseStepSettings):
    """Settings for the Transcription step."""
