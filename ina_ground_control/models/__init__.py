"""
Defines a declarative base class for use with SQLAlchemy ORM.

This module sets up a base class using SQLAlchemy's `declarative_base`
function. The generated base class is intended for defining ORM-mapped
classes. This base is essential for all ORM definitions and serves as
the default base class for mapped models.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
