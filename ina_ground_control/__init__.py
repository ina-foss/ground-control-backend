"""Module ina_ground_control: Provides logging setup and access for the GroundControl service."""
import logging.config
import os
import typing
from importlib import metadata
from importlib.metadata import PackageNotFoundError

from ina_ground_control.models.user_model import UserInfo

# Load logging configuration from file
logging.config.fileConfig("logging.conf") # NOSONAR
# Get logger
logger = logging.getLogger("GroundControl")
logger.setLevel(logging.getLevelName(os.getenv("APP_LOG_LEVEL", "DEBUG").upper()))


def get_application_version(package_name="ina-ground-control"):
    """
    Retrieves the application version for the given package name.

    Args:
        package_name (str): The name of the package to retrieve the version for.
                            Defaults to 'ina-ground-control'.

    Returns:
        str: The version of the application if found.

    Logs:
        INFO: When the version is successfully retrieved.
        WARNING: When the package version cannot be found.
        ERROR: For unexpected exceptions.

    Raises:
        RuntimeError: If an unexpected error occurs while retrieving the version.
    """
    try:
        # Attempt to retrieve the version of the specified package
        version = metadata.version(package_name)
        logger.info("Successfully retrieved version '%s' for package '%s'.", version, package_name)
        return version
    except PackageNotFoundError:
        # Handle the case where the package is not found
        logger.warning("Package '%s' not found. Ensure it is installed.", package_name)
    except Exception as ex:
        # Catch unexpected exceptions and raise a RuntimeError
        logger.error("An unexpected error occurred while retrieving the package version: %s", ex, exc_info=True)
        raise RuntimeError(f"Failed to retrieve version for package '{package_name}'.") from ex

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
        logger.warning("Userinfo is none check sso has userinfo enabled and token has roles: %s", userinfo)
        user = UserInfo(
            email=unk_email,
            roles=[]
        )
    return user
