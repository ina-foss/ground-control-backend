"""Pydantic model defining the settings of an AUTO_SUMMARY step."""

from ina_ground_control.schemas.settings_step_schemas.common_settings import (
    BaseStepSettings,
)


class AutoSummarySettings(BaseStepSettings):
    """Settings for the Auto Summary step.

    Auto summary steps expose no display, synchronization or comment settings.
    """
