from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base


# Синхронный движок для Alembic
sync_url = "postgresql+psycopg2://admin:admin@localhost:5432/twitter"
engine = create_engine(sync_url)

# Асинхронный движок для приложения
async_url = "postgresql+asyncpg://admin:admin@localhost:5432/twitter"
async_engine = create_async_engine(async_url)

Session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)
session = Session()
Base = declarative_base()
