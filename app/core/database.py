import pyodbc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.settings import settings, Environment

# Prevent to pyodbc create internal pool
# https://docs.sqlalchemy.org/en/14/dialects/mssql.html#pyodbc-pooling-connection-close-behavior
pyodbc.pooling = False

# Internal DB
engine_internal = create_async_engine(
    f'postgresql+asyncpg://'
    f'{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}'
    f'@{settings.DATABASE_HOST}:{str(settings.DATABASE_PORT)}'
    f'/{settings.DATABASE_DB}',
    # isolation_level="READ COMMITTED",
    # Prevent connection loss
    pool_use_lifo=True,
    pool_pre_ping=True,
    pool_size=15,
    max_overflow=5,
    pool_recycle=300,
    echo=True if settings.ENVIRONMENT == Environment.DEV else False
)

Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_internal,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()
