# server/alembic/env.py
import sys
import os
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# Load .env explicitly
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")  # sync engine for Alembic

# append src to path so imports work
sys.path.append(str(BASE_DIR / "src"))

# noinspection PyUnusedImports
from src.db.session import Base
from src.domains.auth import models as auth_models
from src.domains.categories import models as categories_models
from src.domains.csv import models as csv_models
from src.domains.rules import models as rules_models
from src.domains.transactions import models as transactions_models

_ = (auth_models, categories_models, csv_models, rules_models, transactions_models)

# Alembic config
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(
        SYNC_DATABASE_URL,
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()