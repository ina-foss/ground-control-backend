"""Factory helpers to build typed step settings from an annotation type.

Mirrors the plugin ``PluginConfigDTO.build`` pattern: a single registry maps
each :class:`AnnotationType` to its dedicated settings model, so the rest of the
codebase never has to branch on the step type. Building a settings payload
validates the provided (possibly partial) data and completes it with the type
defaults, guaranteeing the persisted JSON is always compatible with the step
type.
"""

from typing import Optional, Type

from ina_ground_control.constants.enums import AnnotationType
from ina_ground_control.schemas.settings_step_schemas.auto_summary_settings import (
    AutoSummarySettings,
)
from ina_ground_control.schemas.settings_step_schemas.common_settings import (
    BaseStepSettings,
)
from ina_ground_control.schemas.settings_step_schemas.segmentation_settings import (
    SegmentationSettings,
)
from ina_ground_control.schemas.settings_step_schemas.span_settings import SpanSettings
from ina_ground_control.schemas.settings_step_schemas.transcription_settings import (
    TranscriptionSettings,
)
from ina_ground_control.schemas.settings_step_schemas.video_segmentation_settings import (
    VideoSegmentationSettings,
)

STEP_SETTINGS_BY_TYPE: dict[AnnotationType, Type[BaseStepSettings]] = {
    AnnotationType.SPAN: SpanSettings,
    AnnotationType.VIDEO_SEGMENTATION: VideoSegmentationSettings,
    AnnotationType.SEGMENTATION: SegmentationSettings,
    AnnotationType.AUTO_SUMMARY: AutoSummarySettings,
    AnnotationType.TRANSCRIPTION: TranscriptionSettings,
}


def get_settings_class(
    annotation_type: AnnotationType | str,
) -> Optional[Type[BaseStepSettings]]:
    """Return the settings model bound to ``annotation_type`` (or ``None``)."""
    if isinstance(annotation_type, str):
        annotation_type = AnnotationType(annotation_type)
    return STEP_SETTINGS_BY_TYPE.get(annotation_type)


def build_step_settings(
    annotation_type: AnnotationType | str, data: Optional[dict] = None
) -> Optional[dict]:
    """Validate and complete a settings payload for the given step type.

    - Missing fields are filled with the step type defaults.
    - Step types without a dedicated settings model keep the raw payload,
      preserving backward compatibility for legacy/unknown types.

    Raises:
        pydantic.ValidationError: when the payload is incompatible with the type.
    """
    settings_class = get_settings_class(annotation_type)
    if settings_class is None:
        return data
    model = settings_class.model_validate(data or {})
    return model.model_dump(mode="json")
