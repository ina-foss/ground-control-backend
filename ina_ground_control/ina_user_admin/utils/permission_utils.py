"""Utility helpers for permission and role checking."""


def has_permission(user_roles: list[str], required_permission: str) -> bool:
    """Check if a list of role names contains the required permission.

    Args:
        user_roles: Role names held by the user.
        required_permission: The permission string to look for.

    Returns:
        ``True`` if ``required_permission`` is in ``user_roles``, else ``False``.
    """
    return required_permission in user_roles


def has_any_permission(user_roles: list[str], required_permissions: list[str]) -> bool:
    """Check if a list of role names contains any of the required permissions.

    Args:
        user_roles: Role names held by the user.
        required_permissions: Permissions to check — a match on any one is sufficient.

    Returns:
        ``True`` if at least one permission from ``required_permissions`` is present
        in ``user_roles``, else ``False``.
    """
    return any(p in user_roles for p in required_permissions)


def has_all_permissions(user_roles: list[str], required_permissions: list[str]) -> bool:
    """Check if a list of role names contains all of the required permissions.

    Args:
        user_roles: Role names held by the user.
        required_permissions: Permissions to check — every one must be present.

    Returns:
        ``True`` if every permission in ``required_permissions`` is present in
        ``user_roles``, else ``False``.
    """
    return all(p in user_roles for p in required_permissions)


def filter_roles_by_prefix(roles: list[str], prefix: str) -> list[str]:
    """Filter role names to only those starting with the given prefix.

    Args:
        roles: Full list of role name strings to filter.
        prefix: The prefix string to match at the start of each role name.

    Returns:
        A new list containing only roles whose name starts with ``prefix``.
    """
    return [r for r in roles if r.startswith(prefix)]
