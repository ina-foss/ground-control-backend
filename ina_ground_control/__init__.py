"""Module ina_ground_control: Provides logging setup and access for the GroundControl service."""
import logging.config

# Load logging configuration from file
logging.config.fileConfig("logging.conf")

# Get logger
logger = logging.getLogger("GroundControl")
