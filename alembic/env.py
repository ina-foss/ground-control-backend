from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import alembic_postgresql_enum
import os
import sys

# this is the Alembic Config object, which provides
# access to the values within the.ini file in use.
config = context.config



# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Adjust the system path to include the parent directory of the current script
# This allows us to import modules from the project root
current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir, '..', '..')
sys.path.append(project_root)

# Now, import the Base from your database.py file
from ina_ground_control.database import Base
from ina_ground_control.models.project_model import Project, ProjectStatus, AnnotationType
from ina_ground_control.models.task_model import Task
from ina_ground_control.models.user_model import User
from ina_ground_control.models.prediction_model import Prediction
from ina_ground_control.models.annotation_model import Annotation
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

PG_SERVER = os.getenv('PG_SERVER')
PG_DATABASE = os.getenv('PG_DATABASE')
PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_PORT = os.getenv('PG_PORT')
DATABASE_HOSTNAME = os.getenv('DATABASE_HOSTNAME')

config.set_main_option('sqlalchemy.url', f'{PG_SERVER}://{PG_USERNAME}:{PG_PASSWORD}@{DATABASE_HOSTNAME}:{PG_PORT}/{PG_DATABASE}')
# Set the target_metadata to the metadata of your Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
#... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
