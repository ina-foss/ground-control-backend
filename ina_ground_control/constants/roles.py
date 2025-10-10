"""
This module defines constants for roles, resources, actions, and permissions used in the ina_ground_control system.
It associates permissions and roles for access control across the application.
"""

from enum import Enum
from typing import Dict, List

GROUND_CONTROL = "ground-control"


class Role(str, Enum):
    """
    Enum representing different roles within the ground control system.
    Each role corresponds to specific permissions.
    """

    GC_ADMIN = "GC_ADMIN"
    GC_PROJECT_OWNER = "GC_PROJECT_OWNER"
    GC_ANNOTATOR = "GC_ANNOTATOR"


class Resource(str, Enum):
    """
    Enum representing the various resources within the ground control system.
    Resources can have associated actions defined elsewhere.
    """

    PROJECT = "project"
    ANNOTATION = "annotation"
    MEDIA = "media"
    PLUGIN = "plugin"
    RESSOURCE = "resource"
    STEP = "step"
    TAG = "tag"
    TASK_COMMENT = "taskComment"
    TASK = "task"
    USER = "user"


class Action(str, Enum):
    """
    Enum defining the possible actions that can be performed on resources.
    Actions represent operations like Create, Read, Update, Delete, etc.
    """

    # CRUD ACTIONS
    CREATE = "create"
    READ = "read"
    READ_ALL = "read_all"
    UPDATE = "update"
    DELETE = "delete"
    # Project
    FINISH_PROJECT = "finish"
    # Annotation
    GET_ANNOTATIONS_BY_ID = "get_annotations_by_id"
    UPDATE_ANNOTATION_RESULT = "update_annotation_result"
    FINISH_ANNOTATION = "finish_annotation"
    # Media
    # Plugin
    SEARCH_PLUGINS = "search_plugins"
    # Ressource
    GET_TRANSCRIPTION = "get_transcription"
    # Step
    # Tag
    # TASK_COMMENT
    READ_TASK_COMMENT = "read_task_comment"
    READ_TASK_COMMENTS_BY_TASK_ID = "read_task_comments_by_task_id"
    CREATE_TASK_COMMENT = "create_task_comment"
    UPDATE_TASK_COMMENT = "update_task_comment"
    DELETE_TASK_COMMENT = "delete_task_comment"
    READ_TASK_COMMENTS = ("read_task_comments",)
    # Task
    TASK_INJECT = "task_inject"
    ACTIVATE = "activate"
    UPDATE_EXPIRATION_DATTE = "update_expiration_date"
    # User
    GET_USER_BY_EMAIL = "get_user_by_email"


class Permission(str, Enum):
    """
    Represents permission actions as an enumeration for various resources and operations in the system.

    This class is used to structure and manage permissions related to different
    resources, such as projects, annotations, media, plugins, steps, tags, tasks, users,
    and task comments. Each permission is represented as a string value that combines
    specific elements such as the system name, resource type, and corresponding action.

    :ivar CREATE_PROJECT: Permission string to create a project.
    :type CREATE_PROJECT: str
    :ivar READ_PROJECTS: Permission string to read all projects.
    :type READ_PROJECTS: str
    :ivar READ_PROJECT: Permission string to read a single project.
    :type READ_PROJECT: str
    :ivar DELETE_PROJECT: Permission string to delete a project.
    :type DELETE_PROJECT: str
    :ivar CREATE_ANNOTATION: Permission string to create an annotation.
    :type CREATE_ANNOTATION: str
    :ivar GET_ANNOTATIONS_BY_ID: Permission string to get annotations by ID.
    :type GET_ANNOTATIONS_BY_ID: str
    :ivar UPDATE_ANNOTATION_RESULT: Permission string to update an annotation result.
    :type UPDATE_ANNOTATION_RESULT: str
    :ivar FINISH_ANNOTATION: Permission string to finish an annotation.
    :type FINISH_ANNOTATION: str
    :ivar READ_MEDIA: Permission string to read media.
    :type READ_MEDIA: str
    :ivar CREATE_MEDIA: Permission string to create media.
    :type CREATE_MEDIA: str
    :ivar UPDATE_DATA_MEDIA: Permission string to update media data.
    :type UPDATE_DATA_MEDIA: str
    :ivar DELETE_MEDIA: Permission string to delete media.
    :type DELETE_MEDIA: str
    :ivar READ_MEDIAS: Permission string to read all media.
    :type READ_MEDIAS: str
    :ivar SEARCH_PLUGINS: Permission string to search plugins.
    :type SEARCH_PLUGINS: str
    :ivar READ_PLUGINS: Permission string to read all plugins.
    :type READ_PLUGINS: str
    :ivar CREATE_PLUGIN: Permission string to create a plugin.
    :type CREATE_PLUGIN: str
    :ivar DELETE_PLUGIN: Permission string to delete a plugin.
    :type DELETE_PLUGIN: str
    :ivar READ_PLUGIN: Permission string to read a single plugin.
    :type READ_PLUGIN: str
    :ivar GET_TRANSCRIPTION: Permission string to get a transcription.
    :type GET_TRANSCRIPTION: str
    :ivar READ_STEP: Permission string to read a step.
    :type READ_STEP: str
    :ivar CREATE_STEP: Permission string to create a step.
    :type CREATE_STEP: str
    :ivar UPDATE_DATA_STEP: Permission string to update step data.
    :type UPDATE_DATA_STEP: str
    :ivar DELETE_STEP: Permission string to delete a step.
    :type DELETE_STEP: str
    :ivar READ_STEPS: Permission string to read all steps.
    :type READ_STEPS: str
    :ivar READ_TAG: Permission string to read a tag.
    :type READ_TAG: str
    :ivar UPDATE_TAG: Permission string to update a tag.
    :type UPDATE_TAG: str
    :ivar DELETE_TAG: Permission string to delete a tag.
    :type DELETE_TAG: str
    :ivar READ_TAGS: Permission string to read all tags.
    :type READ_TAGS: str
    :ivar READ_TASK_COMMENT: Permission string to read a task comment.
    :type READ_TASK_COMMENT: str
    :ivar READ_TASK_COMMENTS_BY_TASK_ID: Permission string to read task comments by task ID.
    :type READ_TASK_COMMENTS_BY_TASK_ID: str
    :ivar CREATE_TASK_COMMENT: Permission string to create a task comment.
    :type CREATE_TASK_COMMENT: str
    :ivar UPDATE_TASK_COMMENT: Permission string to update a task comment.
    :type UPDATE_TASK_COMMENT: str
    :ivar DELETE_TASK_COMMENT: Permission string to delete a task comment.
    :type DELETE_TASK_COMMENT: str
    :ivar READ_TASK_COMMENTS: Permission string to read all task comments.
    :type READ_TASK_COMMENTS: str
    :ivar READ_TASK: Permission string to read a task.
    :type READ_TASK: str
    :ivar CREATE_TASK: Permission string to create a task.
    :type CREATE_TASK: str
    :ivar TASK_INJECT: Permission string to inject a task.
    :type TASK_INJECT: str
    :ivar UPDATE_DATA_TASK: Permission string to update task data.
    :type UPDATE_DATA_TASK: str
    :ivar DELETE_TASK: Permission string to delete a task.
    :type DELETE_TASK: str
    :ivar READ_USERS: Permission string to read all users.
    :type READ_USERS: str
    :ivar CREATE_USER: Permission string to create a user.
    :type CREATE_USER: str
    :ivar GET_USER_BY_EMAIL: Permission string to get a user by email.
    :type GET_USER_BY_EMAIL: str
    """

    # Project
    CREATE_PROJECT = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.CREATE.value}"
    READ_PROJECTS = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.READ_ALL.value}"
    READ_PROJECT = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.READ.value}"
    DELETE_PROJECT = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.DELETE.value}"
    FINISH_PROJECT = (
        f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.FINISH_PROJECT.value}"
    )
    # Annotation
    CREATE_ANNOTATION = (
        f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.CREATE.value}"
    )
    GET_ANNOTATIONS_BY_ID = f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.GET_ANNOTATIONS_BY_ID.value}"
    UPDATE_ANNOTATION_RESULT = f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.UPDATE_ANNOTATION_RESULT.value}"
    FINISH_ANNOTATION = (
        f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.FINISH_ANNOTATION.value}"
    )
    # Media
    READ_MEDIA = f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.READ.value}"
    CREATE_MEDIA = f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.CREATE.value}"
    UPDATE_DATA_MEDIA = f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.UPDATE.value}"
    DELETE_MEDIA = f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.DELETE.value}"
    READ_MEDIAS = f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.READ_ALL.value}"
    # Plugin
    SEARCH_PLUGINS = (
        f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.SEARCH_PLUGINS.value}"
    )
    READ_PLUGINS = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.READ_ALL.value}"
    CREATE_PLUGIN = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.CREATE.value}"
    DELETE_PLUGIN = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.DELETE.value}"
    READ_PLUGIN = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.READ.value}"
    # Ressource
    GET_TRANSCRIPTION = (
        f"{GROUND_CONTROL}:{Resource.RESSOURCE.value}:{Action.GET_TRANSCRIPTION.value}"
    )
    # Step
    READ_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.READ.value}"
    CREATE_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.CREATE.value}"
    UPDATE_DATA_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.UPDATE.value}"
    DELETE_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.DELETE.value}"
    READ_STEPS = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.READ_ALL.value}"
    # Tag
    READ_TAG = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.READ.value}"
    UPDATE_TAG = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.UPDATE.value}"
    DELETE_TAG = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.DELETE.value}"
    READ_TAGS = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.READ_ALL.value}"
    # TASK_COMMENT
    READ_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.READ_TASK_COMMENT.value}"
    READ_TASK_COMMENTS_BY_TASK_ID = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.READ_TASK_COMMENTS_BY_TASK_ID.value}"
    CREATE_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.CREATE_TASK_COMMENT.value}"
    UPDATE_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.UPDATE_TASK_COMMENT.value}"
    DELETE_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.DELETE_TASK_COMMENT.value}"
    READ_TASK_COMMENTS = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.READ_TASK_COMMENTS.value}"
    # Task
    READ_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.READ.value}"
    CREATE_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.CREATE.value}"
    TASK_INJECT = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.TASK_INJECT.value}"
    UPDATE_DATA_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.UPDATE.value}"
    DELETE_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.DELETE.value}"
    ACTIVATE_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.ACTIVATE.value}"
    UPDATE_EXPIRATION_DATTE = (
        f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.UPDATE_EXPIRATION_DATTE.value}"
    )
    # User
    READ_USERS = f"{GROUND_CONTROL}:{Resource.USER.value}:{Action.READ_ALL.value}"
    CREATE_USER = f"{GROUND_CONTROL}:{Resource.USER.value}:{Action.CREATE.value}"
    GET_USER_BY_EMAIL = (
        f"{GROUND_CONTROL}:{Resource.USER.value}:{Action.GET_USER_BY_EMAIL.value}"
    )

    @staticmethod
    def get_value_if_exists(value: str):
        """
        Return the Permission enum value if it exists.

        Args:
            value (str): The value to look for in the Permission enum.

        Returns:
            Permission: The corresponding Permission enum value if it exists.
            None: If the value does not exist in the Permission enum.
        """
        for permission in Permission:
            if permission.value == value:
                return permission
        return None

    @staticmethod
    def has(value: str) -> bool:
        """
        Check if the given value exists in the Permission enum.

        Args:
            value (str): The value to check.

        Returns:
            bool: True if the value exists in the Permission enum; False otherwise.
        """
        return value in (e.value for e in Permission)


# Define role-based permissions using the Permission Enum
ROLE_PERMISSIONS: Dict[str, List[Permission]] = {
    Role.GC_ADMIN: [
        Permission.CREATE_PROJECT.value,
        Permission.DELETE_PROJECT.value,
        Permission.DELETE_STEP.value,
        Permission.DELETE_PLUGIN.value,
    ],
    Role.GC_PROJECT_OWNER: [],
    Role.GC_ANNOTATOR: [],
}
