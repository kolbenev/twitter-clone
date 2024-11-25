from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


# Асинхронное подключение
async_database_url = "postgresql+asyncpg://test:test@localhost:5432/test_twitter"
async_engine = create_async_engine(url=async_database_url, echo=True)
async_Session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession,
)
async_session = async_Session()

# Синхронное подключение
sync_database_url = "postgresql+psycopg://test:test@localhost:5432/test_twitter"
sync_engine = create_engine(url=sync_database_url, echo=True)
sync_Session = sessionmaker(bind=sync_engine)
sync_session = sync_Session()