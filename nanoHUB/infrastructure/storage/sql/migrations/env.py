from nanoHUB.application import Application
from nanoHUB.infrastructure.storage.sql import model
from alembic import config as alembic_config, command
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = model.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# application = Application.get_instance()
# db_engine = application.new_db_engine('ANALYTICS_1')


# with db_engine.begin() as connection:
#     config.attributes['connection'] = connection
#     command.upgrade(config, "head")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    if hasattr(config, 'connection'):
        connection = config.connection

    else:

        application = Application.get_instance()
        db_engine = application.new_db_engine('ANALYTICS_1')

        connection = db_engine.connect()
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        if not hasattr(config, 'connection'):
            connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
