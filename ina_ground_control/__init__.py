"""Module ina_ground_control: Provides logging setup and access for the GroundControl service."""

import logging.config
import typing

from ina_ground_control.config.settings import Settings
from ina_ground_control.models.user_model import UserInfo
from ina_ground_control.utils.application_helpers import (
    get_application_version,
    setup_logging,
)

settings = Settings()
settings.version = get_application_version()

# Set up logging
setup_logging()

# Get logger
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level.upper())

from functools import cache

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def get_db():
    """
    Get a new database session and close it after use.

    Yields:
        Session: A SQLAlchemy session object.
    """
    db = SessionLocal()
    db.execute(text("SET TRANSACTION READ WRITE"))
    try:
        yield db
    finally:
        db.close()


@cache
def get_engine(db_string: str):
    """Returns a SQLAlchemy engine instance, cached for reuse."""
    try:
        engine = create_engine(db_string, pool_pre_ping=True, echo=settings.debug)
        logger.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logger.exception("Failed to create database engine : %s", str(e))
        raise


async def map_user(userinfo: typing.Dict[str, typing.Any]) -> UserInfo:
    """
    Maps user information received from Keycloak to a User model instance.

    Args:
        userinfo (Dict[str, Any]): The user information dictionary.

    Returns:
        UserInfo: An instance of the UserInfo model.
    """

    # Map the fields from the userinfo to the UserInfo model
    unk_email = "unknown@unknown.com"
    if userinfo is not None:
        user = UserInfo(
            email=userinfo.get("email", unk_email),
            roles=userinfo.get("roles", []),
        )
    else:
        logger.warning(
            "Userinfo is none check sso has userinfo enabled and token has roles: %s",
            userinfo,
        )
        user = UserInfo(email=unk_email, roles=[])
    return user


SessionLocal = sessionmaker(  # pylint: disable=invalid-name
    autocommit=False,
    autoflush=False,
    bind=get_engine(str(settings.get_db_connection_string())),
)
