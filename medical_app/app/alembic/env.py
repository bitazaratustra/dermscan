# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import create_engine
from app.models.base import Base
from app.database import SQLALCHEMY_DATABASE_URL
from alembic import context

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_engine(SQLALCHEMY_DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
