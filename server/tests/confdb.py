from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, async_session


database_url = "postgresql+asyncpg://test:test@localhost:5432/test_twitter"
engine = create_async_engine(database_url, echo=True)
Session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
session = Session()

# async def get_session():
#     async with Session as session:
#         yield session