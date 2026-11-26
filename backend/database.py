import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Brak zmiennej środowiskowej DATABASE_URL")

# 1. Asynchroniczny silnik zamiast zwykłego create_engine
engine = create_async_engine(DATABASE_URL)

# 2. Asynchroniczna fabryka sesji zamiast zwykłego sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


# 3. Asynchroniczny generator sesji dla endpointów FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# synchroniczne podjescie
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
#
# DATABASE_URL = os.getenv(
#     "DATABASE_URL", "postgresql+asyncpg://cs2user:cs2password@db:5432/cs2market"
# )
#
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
