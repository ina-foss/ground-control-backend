from enum import Enum
from typing import Dict, List

GROUND_CONTROL = "ground-control"

class Role(str, Enum):
    GC_ADMIN = "GC_ADMIN"
    GC_PROJECT_OWNER = "GC_PROJECT_OWNER"
    GC_ANNOTATOR = "GC_ANNOTATOR"

class Resource(str, Enum):
    PROJECT = "project"
    ANNOTATION = "annotation"
    MEDIA = "media"
    PLUGIN = "plugin"
    RESSOURCE = "resource"
    STEP = "step"
    TAG = "tag"
    TASK_COMMENT= "taskComment"
    TASK = "task"
    USER = "user"

class Action(str, Enum):
    #Project
    CREATE_PROJECT = "create_project"
    READ_PROJECTS= "read_projects"
    READ_PROJECT = "read_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    #Annotation
    CREATE_ANNOTATION= "create_annotation"
    GET_ANNOTATIONS_BY_ID = "get_annotations_by_id"
    UPDATE_ANNOTATION_RESULT = "update_annotation_result"
    FINISH_ANNOTATION = "finish_annotation"
    #Media
    READ_MEDIA = "read_media"
    CREATE_MEDIA = "create_media"
    UPDATE_DATA_MEDIA = "update_data_media"
    DELETE_MEDIA = "delete_media"
    READ_MEDIAS = "read_medias"
    #Plugin
    SEARCH_PLUGINS = "search_plugins"
    READ_PLUGINS = "read_plugins"
    CREATE_PLUGIN = "create_plugin"
    DELETE_PLUGIN = "delete_plugin"
    READ_PLUGIN = "read_plugin"
    #Ressource
    GET_TRANSCRIPTION = "get_transcription"
    #Step
    READ_STEP = "read_step"
    CREATE_STEP = "create_step"
    UPDATE_DATA_STEP = "update_data_step"
    DELETE_STEP = "delete_step"
    READ_STEPS = "read_steps"
    #Tag
    READ_TAG = "read_tag"
    UPDATE_TAG = "update_tag"
    DELETE_TAG = "delete_tag"
    READ_TAGS = "read_tags"
    #TASK_COMMENT
    READ_TASK_COMMENT = "read_task_comment"
    READ_TASK_COMMENTS_BY_TASK_ID = "read_task_comments_by_task_id"
    CREATE_TASK_COMMENT = "create_task_comment"
    UPDATE_TASK_COMMENT = "update_task_comment"
    DELETE_TASK_COMMENT = "delete_task_comment"
    READ_TASK_COMMENTS = "read_task_comments"
    #Task
    READ_TASK = "read_task"
    CREATE_TASK = "create_task"
    TASK_INJECT = "task_inject"
    UPDATE_DATA_TASK = "update_data_task"
    #User
    READ_USERS = "read_users"
    CREATE_USER = "create_user"
    GET_USER_BY_EMAIL = "get_user_by_email"

class Permission(str, Enum):
    #Project
    CREATE_PROJECT = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.CREATE_PROJECT.value}"
    READ_PROJECTS = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.READ_PROJECTS.value}"
    READ_PROJECT = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.READ_PROJECT.value}"
    DELETE_PROJECT = f"{GROUND_CONTROL}:{Resource.PROJECT.value}:{Action.DELETE_PROJECT.value}"
    #Annotation
    CREATE_ANNOTATION= f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.CREATE_ANNOTATION.value}"
    GET_ANNOTATIONS_BY_ID = f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.GET_ANNOTATIONS_BY_ID.value}"
    UPDATE_ANNOTATION_RESULT = f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.UPDATE_ANNOTATION_RESULT.value}"
    FINISH_ANNOTATION = f"{GROUND_CONTROL}:{Resource.ANNOTATION.value}:{Action.FINISH_ANNOTATION.value}"
    #Media
    READ_MEDIA = f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.READ_MEDIA.value}"
    CREATE_MEDIA =  f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.CREATE_MEDIA.value}"
    UPDATE_DATA_MEDIA =  f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.UPDATE_DATA_MEDIA.value}"
    DELETE_MEDIA =  f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.DELETE_MEDIA.value}"
    READ_MEDIAS =  f"{GROUND_CONTROL}:{Resource.MEDIA.value}:{Action.READ_MEDIAS.value}"
    #Plugin
    SEARCH_PLUGINS =  f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.SEARCH_PLUGINS.value}"
    READ_PLUGINS = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.READ_PLUGINS.value}"
    CREATE_PLUGIN = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.CREATE_PLUGIN.value}"
    DELETE_PLUGIN = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.DELETE_PLUGIN.value}"
    READ_PLUGIN = f"{GROUND_CONTROL}:{Resource.PLUGIN.value}:{Action.READ_PLUGIN.value}"
    #Ressource
    GET_TRANSCRIPTION = f"{GROUND_CONTROL}:{Resource.RESSOURCE.value}:{Action.GET_TRANSCRIPTION.value}"
    #Step
    READ_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.READ_STEP.value}"
    CREATE_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.CREATE_STEP.value}"
    UPDATE_DATA_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.UPDATE_DATA_STEP.value}"
    DELETE_STEP = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.DELETE_STEP.value}"
    READ_STEPS = f"{GROUND_CONTROL}:{Resource.STEP.value}:{Action.READ_STEPS.value}"
    #Tag
    READ_TAG = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.READ_TAG.value}"
    UPDATE_TAG = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.UPDATE_TAG.value}"
    DELETE_TAG = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.DELETE_TAG.value}"
    READ_TAGS = f"{GROUND_CONTROL}:{Resource.TAG.value}:{Action.READ_TAGS.value}"
    #TASK_COMMENT
    READ_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.READ_TASK_COMMENT.value}"
    READ_TASK_COMMENTS_BY_TASK_ID = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.READ_TASK_COMMENTS_BY_TASK_ID.value}"
    CREATE_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.CREATE_TASK_COMMENT.value}"
    UPDATE_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.UPDATE_TASK_COMMENT.value}"
    DELETE_TASK_COMMENT = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.DELETE_TASK_COMMENT.value}"
    READ_TASK_COMMENTS = f"{GROUND_CONTROL}:{Resource.TASK_COMMENT.value}:{Action.READ_TASK_COMMENTS.value}"
    #Task
    READ_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.READ_TASK.value}"
    CREATE_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.CREATE_TASK.value}"
    TASK_INJECT = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.TASK_INJECT.value}"
    UPDATE_DATA_TASK = f"{GROUND_CONTROL}:{Resource.TASK.value}:{Action.UPDATE_DATA_TASK.value}"
    #User
    READ_USERS = f"{GROUND_CONTROL}:{Resource.USER.value}:{Action.READ_USERS.value}"
    CREATE_USER = f"{GROUND_CONTROL}:{Resource.USER.value}:{Action.CREATE_USER.value}"
    GET_USER_BY_EMAIL = f"{GROUND_CONTROL}:{Resource.USER.value}:{Action.GET_USER_BY_EMAIL.value}"

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