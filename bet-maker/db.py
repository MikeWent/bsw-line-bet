from os import getenv

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://" + getenv("DATABASE"),
    echo=True,
)

# async_sessionmaker: a factory for new AsyncSession objects.
# expire_on_commit - don't expire objects after transaction commit
async_session = async_sessionmaker(engine, expire_on_commit=False)
