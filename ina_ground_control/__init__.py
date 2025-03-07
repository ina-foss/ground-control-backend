"""Module ina_ground_control: Provides logging setup and access for the GroundControl service."""
import logging.config
import os

# Load logging configuration from file
logging.config.fileConfig("logging.conf")
# Get logger
logger = logging.getLogger("GroundControl")
logger.setLevel(logging.getLevelName(os.getenv("APP_LOG_LEVEL", "DEBUG").upper()))
