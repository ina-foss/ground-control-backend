from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    userid: int
    email: EmailStr
    role: str
    created_at: Optional[datetime]


    class Config:
        orm_mode = True