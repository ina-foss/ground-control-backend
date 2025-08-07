"""
INA Ground Control API: Configuration
"""

from dynaconf import Dynaconf

settings = Dynaconf(
    root_path="ina_ground_control",
    settings_files=["settings*.yaml", ".secrets.yaml"],
    envvar_prefix="INA_GROUND_CONTROL",
    env_switcher="INA_GROUND_CONTROL_ENV",
    environments=True,
    load_dotenv=True,
    merge_enabled=True,
)
