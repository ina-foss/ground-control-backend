"""
INA Ground Control API: Configuration
"""

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="INA_GROUND_CONTROL",
    environments=True,
    load_dotenv=True,
    env_switcher="INA_GROUND_CONTROL_ENV"
)
