"""
Defines the declarative base class shared by SQLAlchemy ORM and SQLModel models.

Historically this module exposed a plain ``declarative_base()``. As part of the
incremental migration to SQLModel (see ``SQLMODEL_MIGRATION.md``), the ``Base``
is now generated from SQLModel's own registry via
``SQLModel._sa_registry.generate_base()``.

Why this matters:
    * ``Base.metadata is SQLModel.metadata`` -> a single ``MetaData`` holds the
      tables of BOTH legacy declarative models (``class X(Base)``) and migrated
      SQLModel models (``class X(SQLModel, table=True)``). Alembic
      (``target_metadata = Base.metadata``) and the test suite
      (``Base.metadata.create_all``) therefore keep seeing every table during
      the transition.
    * A single class registry -> relationships declared by string name (e.g.
      ``relationship("User")`` / ``Relationship(back_populates=...)``) resolve
      across the two styles, so a migrated model and a not-yet-migrated model
      can still point at each other.

This lets models be migrated one at a time with no big-bang cutover.
"""

from sqlmodel import SQLModel

# ``generate_base()`` returns a declarative base bound to SQLModel's registry
# and metadata. Legacy models keep subclassing ``Base`` unchanged; migrated
# models subclass ``SQLModel`` directly. Both share the same registry/metadata.
Base = SQLModel._sa_registry.generate_base()  # pylint: disable=protected-access
