Roles Guide
===========

This guide provides an overview of how roles and permissions function within the system and how to configure them.

Overview
--------

The system implements **Role-Based Access Control (RBAC)** with two key components:

1. **Global Roles**: Define a user’s general level of access. The primary roles include:

   - ``GC_ADMIN``
   - ``GC_PROJECT_OWNER``
   - ``GC_ANNOTATOR``

2. **Permissions**: Determine specific actions a user can perform within the system.

Both **roles and permissions** are stored in the **roles claim** within the authentication token.

Understanding Permissions
-------------------------

Permissions specify which actions a user is allowed to perform. They are assigned based on the user's **global role** and follow a structured naming convention:

``<project_name>:<resource_name>:<action_name>``

Example:
~~~~~~~~

To grant a user permission to create a project, they must have the following role in their token:

``ground-control:project:create_project``

Checking Permissions
====================

The ``CheckPermissions`` function verifies whether a user's **roles** include the required **permission**.

Match Strategy
--------------

A **match strategy** determines how permissions are validated when multiple permissions are required.
It defines whether **all** conditions must be met (``AND``) or if at least **one** condition is sufficient (``OR``).

- **``MatchStrategy.AND``** → The user **must** have **all** the required permissions.
- **``MatchStrategy.OR``** → The user **must** have **at least one** of the required permissions.

Example in Code:
~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi_keycloak_middleware import CheckPermissions, MatchStrategy, AuthorizationResult
   from ina_ground_control.constants.roles import Permission

   @app.get("/delete_project")
   def delete_project(
       ....
       _authorization_result: AuthorizationResult = Depends(
           CheckPermissions(
               [Permission.DELETE_PROJECT.value],
               match_strategy=MatchStrategy.AND
           )
       )
   ):
       ....  # Processing logic

Explanation:
~~~~~~~~~~~~

- The function verifies if the user has the required permissions to delete a project.
- If the user doesn't have the required permission, they will receive an error **403 Forbidden** with details:

  .. code-block:: json

     {"detail": "Permission denied"}

- With ``MatchStrategy.AND``, the user must have **all** assigned permissions.
- With ``MatchStrategy.OR``, the user only needs **one** of the required permissions.

Keycloak Configuration
======================

To add a permission in Keycloak, follow these steps:

1. Navigate to **Clients** → Select **account**.
2. Go to the **Roles** tab.
3. Click on the **Create Role** button to add a new permission.
4. In the **Role Name** field, enter your permission in the format:

   ``<project_name>:<resource_name>:<action_name>``

5. Click **Save**.
6. Navigate to **Users**.
7. Select the user (e.g., **admin**).
8. Go to the **Role Mapping** tab.
9. Click on **Assign Role**.
10. In the pop-up, filter by **Clients**, select the required roles, and click **Assign**.

Verification:
~~~~~~~~~~~~~

To verify the assigned roles, log into your application and decode your authentication token to ensure the new roles appear.

