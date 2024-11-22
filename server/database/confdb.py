from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker

url = "postgresql+asyncpg://admin:admin@database/twitter"
