"""Base repository exposing shared database session access."""

from sqlmodel import Session


class BaseRepository:
    """Base repository class providing database session access.

    All concrete repositories should inherit from this class and use
    ``self._db_session`` to interact with the database.

    Attributes:
        _db_session: The SQLModel/SQLAlchemy session used for database operations.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialise the repository with a database session.

        Args:
            db_session: An active SQLModel ``Session`` instance.
        """
        self._db_session = db_session
