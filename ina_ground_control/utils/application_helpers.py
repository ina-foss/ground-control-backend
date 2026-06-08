"""Helper utilities for the MCP server."""

import importlib
import importlib.metadata
import logging
import logging.config
import os
from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

# Use a local logger instead of importing from the main package
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """
    Configures logging for the application by either loading a configuration file or falling back
    to basic logging.

    :raises FileNotFoundError: If the logging configuration file is missing and not handled explicitly.
    """
    # Load logging configuration from file - make path relative to project root
    project_root = Path(__file__).parent.parent
    logging_conf_path = project_root / "logging.conf"

    if logging_conf_path.exists():
        logging.config.fileConfig(str(logging_conf_path))  # NOSONAR
    else:
        # Fallback to basic logging if config file not found
        logging.basicConfig(level=logging.INFO)  # NOSONAR

    # Adjust third-party library logging levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


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
        version = importlib.metadata.version(package_name)
        logger.info(
            "Successfully retrieved version '%s' for package '%s'.",
            version,
            package_name,
        )
        return version
    except importlib.PackageNotFoundError:
        # Handle the case where the package is not found
        logger.warning("Package '%s' not found. Ensure it is installed.", package_name)
        return "0.0.1"  # Return a default version instead of None
    except Exception as ex:
        # Catch unexpected exceptions and raise a RuntimeError
        logger.error(
            "An unexpected error occurred while retrieving the package version: %s",
            ex,
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to retrieve version for package '{package_name}'."
        ) from ex


# Mount the static directory
# Mount static directories only if they exist
def mount_static_directory(
    application: FastAPI, path: str, directory: str, name: str
) -> None:
    """Mount a static directory only if it exists."""
    if os.path.exists(directory) and os.path.isdir(directory):
        application.mount(path, StaticFiles(directory=directory), name=name)
        logger.info("Mounted static directory: %s at %s", directory, path)
    else:
        logger.warning(
            "Static directory '%s' does not exist. Skipping mount for %s",
            directory,
            path,
        )
