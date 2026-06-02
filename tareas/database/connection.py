import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Carga .env desde la raiz del proyecto y, como respaldo, desde tareas/.
ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
LOCAL_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ROOT_ENV_PATH if ROOT_ENV_PATH.exists() else LOCAL_ENV_PATH)


def _normalize_driver(driver: str | None) -> str:
    if not driver:
        return "postgresql+asyncpg"
    if driver in {"postgres", "postgresql"}:
        return "postgresql+asyncpg"
    if driver.startswith("postgresql+") and "asyncpg" not in driver:
        return "postgresql+asyncpg"
    return driver


DB_DRIVER = _normalize_driver(os.getenv("DB_DRIVER"))
DB_USER = os.getenv("DB_USER", "tareas_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tareas_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "tareas_db")

DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session():
    async with async_session_maker() as session:
        yield session


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)