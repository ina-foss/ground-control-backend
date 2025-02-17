from enum import Enum

class Resource(str, Enum):
    PROJECT = "project"
    ANNOTATION = "annotation"
    ANNOTATION_TASK_ASSOCIATION = "annotation_task_association"
    MEDIA_MODEL = "media_model"
    MEDIA_PROJECT_ASSOCIATION = "media_project_association"
    PLUGIN = "plugin"
    STEP = "step"
    TAG_PROJECT_ASSOCIATION = "tag_project_association"
    TASK_COMMENT_ASSOCIATION = "task_comment_association"
    TASK = "task"

class Role(str, Enum):
    ADMIN = "GC_ADMIN"
    PROJECT_OWNER = "project_owner"
    ANNOTATOR = "annotator"

class Action(str, Enum):
    #Project
    CREATE_PROJECT = "create_project"
    READ_PROJECT = "read_project"
    DELETE_PROJECT = "delete_project"
