from typing import Optional
from pydantic import BaseModel

class PluginAutocompleteValueDTO(BaseModel):
    id: Optional[str]
    extId: Optional[str]
    label: Optional[str]
