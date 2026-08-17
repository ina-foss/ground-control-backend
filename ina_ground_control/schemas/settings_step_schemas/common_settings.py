"""Base and common Pydantic models shared by every typed step settings model."""

from pydantic import BaseModel, ConfigDict, Field

from ina_ground_control.constants.enums import LaunchMode


class DisplaySettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    span: bool = True
    tc_bloc: bool = True
    tc_segment: bool = False
    segment_number: bool = False


class SynchronizationSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_to_transcription: bool = True
    transcription_to_player: bool = True
    loop_segment: bool = False
    launch_mode: LaunchMode = LaunchMode.CTRL_CLICK
    before_word: int = 2
    after_word: int = 2


class BaseStepSettings(BaseModel):
    """Common base class shared by every typed step settings model.

    It intentionally carries no field so step types without display or
    synchronization options (e.g. AUTO_SUMMARY) can inherit from it directly.
    Unknown keys are rejected to keep a settings JSON always compatible with
    the step type.
    """

    model_config = ConfigDict(extra="forbid")


class DisplayableStepSettings(BaseStepSettings):
    """Base settings for step types exposing display / synchronization / comments."""

    display: DisplaySettings = Field(default_factory=DisplaySettings)
    synchronization: SynchronizationSettings = Field(
        default_factory=SynchronizationSettings
    )
    comments: bool = True
