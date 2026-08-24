"""Pydantic models defining the enums value of a SPAN step settings."""

from enum import Enum


class SpanAction(str, Enum):
    """Enum for span actions."""

    ADD = "add"
    """If the user can add a new span in the text """
    EDIT_PROPERTIES = "edit_properties"
    """ If the user can edit the properties of a span (its plugin's values) """
    EDIT_EDGES = "edit_edges"
    """ If the user can edit the edges of a span by dragging them to a new word """
    REMOVE = "remove"
    """ If the user can remove an existing span """
