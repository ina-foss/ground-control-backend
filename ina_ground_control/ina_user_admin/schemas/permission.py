"""Pydantic schemas for permission data transfer objects."""

from pydantic import BaseModel


class PermissionDTO(BaseModel):
    """Generic permission data transfer object.

    Used to communicate a set of roles, actions, and resources associated
    with a user or token. All fields default to empty lists.

    Attributes:
        roles: List of role names held by the subject.
        actions: List of permitted action strings.
        resources: List of permitted resource identifiers.
    """

    roles: list[str] = []
    actions: list[str] = []
    resources: list[str] = []
