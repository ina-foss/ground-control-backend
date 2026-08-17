"""Pydantic model defining the settings of a SEGMENTATION step."""

from pydantic import Field

from ina_ground_control.schemas.settings_step_schemas.common_settings import (
    DisplayableStepSettings,
    DisplaySettings,
)


class SegmentationSettings(DisplayableStepSettings):
    display: DisplaySettings = Field(
        default_factory=lambda: DisplaySettings(
            tc_bloc=True,
            tc_segment=False,
            segment_number=False,
        )
    )
