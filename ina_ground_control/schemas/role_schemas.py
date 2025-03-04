
from pydantic import BaseModel

from ina_ground_control.constants.roles import Permission


class Role(BaseModel):
    permissions: Permission
