from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBaseDto(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: Optional[datetime]


    class Config:
        orm_mode = True