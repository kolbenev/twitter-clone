from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from server.database.getter_variables import DB_PASSWORD, DB_NAME, DB_USER, DB_HOST


# Синхронный движок для Alembic
sync_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(sync_url)

# Асинхронный движок для приложения
async_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
async_engine = create_async_engine(async_url)

Session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)
session = Session()
Base = declarative_base()
