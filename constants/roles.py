from enum import Enum
from typing import Set, Dict

class Resource(str, Enum):
    ANNOTATION = "annotation"
    ANNOTATION_TASK_ASSOCIATION = "annotation_task_association"
    MEDIA_MODEL = "media_model"
    MEDIA_PROJECT_ASSOCIATION = "media_project_association"
    PLUGIN = "plugin"
    STEP = "step"
    TAG_PROJECT_ASSOCIATION = "tag_project_association"
    TASK_COMMENT_ASSOCIATION = "task_comment_association"
    TASK = "task"
    PROJECT = "project"


class Role(str, Enum):
    ADMIN = "admin"
    PROJECT_OWNER = "project_owner"
    ANNOTATOR = "annotator"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class RolePermissions:
    ROLE_PERMISSIONS: Dict[Role, Dict[Resource, Set[Permission]]] = {
        Role.ADMIN: {
            Resource.TASK: {Permission.CREATE, Permission.EXPORT, Permission.DELETE, Permission.UPDATE, Permission.READ},
            Resource.PROJECT: {Permission.CREATE, Permission.DELETE, Permission.UPDATE, Permission.READ}
        },
        Role.PROJECT_OWNER: {
            Resource.TASK: {Permission.CREATE, Permission.EXPORT, Permission.READ},
            Resource.PROJECT: {Permission.UPDATE, Permission.READ}
        },
        Role.ANNOTATOR: {
            Resource.TASK: {Permission.READ, Permission.UPDATE},
            Resource.PROJECT: {Permission.READ}
        }
    }

    @staticmethod
    def get_permissions(role: Role, resource: Resource) -> Set[Permission]:
        return RolePermissions.ROLE_PERMISSIONS.get(role, {}).get(resource, set())

    @staticmethod
    def check_permission(role: Role, resource: Resource, permission: Permission) -> bool:
        return permission in RolePermissions.get_permissions(role, resource)
