"""
This module defines enums for the project management application.

Enums:
    - InOutEnum: Represents the two types of relations between tasks and annotations (IN/OUT).
    - MediaType: Represents the media types, such as MP4 or HLS.
    - TypePlugin: Represents the different types of plugins used within the application.
    - DisplayZone: Represents the various zones available for displaying plugins.
    - DistributionMode: Describes task distribution modes (STATIC/DYNAMIC).
    - Status: Represents the possible statuses for annotations, tasks, steps, and projects.
    - AnnotationType: Represents the types of annotations (e.g., segmentation, transcription).
    - TaskDataType: Represents data types of tasks (e.g., LDD, Amalia).
"""

from enum import Enum


class InOutEnum(str, Enum):
    """
    Enum representing the two types of relation between Task and Annotation.

    Attributes
    ----------
    IN (str): The annotation is the initial data of the task,
              which can either come from an algorithm or a previous annotation.
    OUT (str): The annotation is the result of the task, containing the user's work.
    """

    IN = "in"
    OUT = "out"


class MediaType(str, Enum):
    """
    Enum representing the different types a media can have.

    Attributes:
        MP4 (str): The media is a mp4 file.
        HLD (str): The project is a hls file.
    """

    MP4 = "mp4"
    HLS = "hls"
    MP3 = "mp3"


class TypePlugin(str, Enum):
    """
        Enum representing the different plugin types.

        Values:
            LABEL: Label plugin
            AUTOCOMPLETE: List with autocomplete functionality.
            LIST_ITEMS: Displays tags and list of items.
            SUGGESTION_LIST: Interactive suggestion block.
    .       INPUT_LABEL: Simple text input field.
    """

    LABEL = "label"  # Représente un plugin label
    AUTOCOMPLETE = "autocomplete"  # Présente une liste avec auto-complétion
    LIST_ITEMS = "listitems"  # Affiche des tags et une liste d'éléments
    SUGGESTION_LIST = "suggestionlist"  # Bloc de suggestions interactives
    INPUT_LABEL = "inputlabel"  # Affiche un champ de saisie de texte simple
    ENTITY_LIST_INPUT = "entitylistinput"  # Affiche une ligne  avec un champ de saisie simple et une liste de choix


class DisplayZone(str, Enum):
    """
    Enum representing the different display zones available for a plugin.

    Attributes:
        BLOC (str): Represents a standalone block zone.
        SPAN_MODAL_LEFT (str): Represents a modal that spans the left side.
        SPAN_MODAL_LEFT_SEGMENT (str): Represents a modal that spans the left side.
        SPAN_MODAL_RIGHT (str): Represents a modal that spans the right side.
        GROUP_MODAL (str): Represents a grouped modal zone for multiple plugins.
    """

    BLOC = "bloc"
    SPAN_MODAL_LEFT = "span_modal_left"
    SPAN_MODAL_LEFT_SEGMENT = "span_modal_left_segment"
    SPAN_MODAL_RIGHT = "span_modal_right"
    GROUP_MODAL = "group_modal"


class DistributionMode(str, Enum):
    """
    Enum describing the different way of distributing task among users

    Attributes
    ----------
        STATIC (str):
        DYNAMIC (str):
    """

    STATIC = "static"
    DYNAMIC = "dynamic"


class Status(str, Enum):
    """
    Enum representing the different statuses an annotation, task, step, and project can have.
    """

    DRAFT = "draft"
    IN_PROGRESS = "in-progress"
    PENDING = "pending"
    SKIPPED = "skipped"
    DONE = "done"
    ARCHIVED = "archived"


class AnnotationType(str, Enum):
    """
    Enum representing the different types of annotations.
    """

    SEGMENTATION = "segmentation"
    TRANSCRIPTION = "transcription"
    SPAN = "span"
    AUTO_SUMMARY = "auto-summary"
    VIDEO_SEGMENTATION = "video-segmentation"


class TaskDataType(str, Enum):
    """
    Enum representing the different datatypes of tasks.

    Attributes:
        LDD (str): The annotation type for ldd tasks.
        AMALIA (str): The annotation type for amalia tasks.
    """

    LDD = "ldd"
    AMALIA = "amalia"
