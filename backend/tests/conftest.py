"""
GripWise Backend Tests — pytest configuration.

Uses SQLite in-memory for fast, dependency-free testing.
No PostgreSQL required for tests.
"""
import os
import tempfile
from pathlib import Path
from urllib.parse import quote
os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"
os.environ["INFERENCE_PROVIDER"] = "mock"

_TEST_RUNTIME = tempfile.TemporaryDirectory(prefix="gripwise-pytest-")
_TEST_RUNTIME_PATH = Path(_TEST_RUNTIME.name)
_TEST_DB_PATH = (_TEST_RUNTIME_PATH / "test.db").as_posix()
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{quote(_TEST_DB_PATH, safe='/:')}"
os.environ["DATABASE_URL_SYNC"] = f"sqlite:///{quote(_TEST_DB_PATH, safe='/:')}"
os.environ["IMAGE_DIR"] = str(_TEST_RUNTIME_PATH / "test_uploads")

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event

from backend.main import app
from backend.database import Base, engine as app_engine, get_db


TEST_DB_URL = os.environ["DATABASE_URL"]
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    await app_engine.dispose()
    _TEST_RUNTIME.cleanup()


@pytest.fixture
async def db_session():
    async with TestSession() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
