import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.db.models import Base
from app.db.session import get_db
from app.main import app
from app.queue import get_queue


class FakeQueue:
    def __init__(self) -> None:
        self.jobs: list[tuple] = []

    async def enqueue_job(self, name: str, *args, **kwargs) -> None:
        self.jobs.append((name, args, kwargs))


@pytest.fixture
def settings() -> Settings:
    return Settings(database_url="sqlite+aiosqlite:///:memory:", auth_mode="password", allow_signup=True)


@pytest.fixture
def queue() -> FakeQueue:
    return FakeQueue()


@pytest.fixture
async def client(settings: Settings, queue: FakeQueue):
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def _db():
        async with sessions() as s:
            yield s

    async def _queue():
        return queue

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_queue] = _queue
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()
