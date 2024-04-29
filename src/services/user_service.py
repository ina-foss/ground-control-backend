from sqlalchemy.orm import Session
from src.models.user_model import *

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
