"""Shared test fixtures. Uses a dedicated test database in the same MySQL."""

import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.session import get_async_session
from app.main import app
from app.models.base import Base

# Build test DB URL: replace database name with test variant
_prod_url = settings.DB_URL
_test_url = _prod_url.rsplit("/", 1)[0] + "/game_boosting_test"

_engine = create_async_engine(_test_url, echo=False)
_session_factory = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create test database and all tables once per session."""
    # Create the test database if it doesn't exist
    admin_url = _prod_url.rsplit("/", 1)[0] + "/mysql"
    admin_engine = create_async_engine(admin_url, echo=False)
    async with admin_engine.begin() as conn:
        await conn.execute(text("CREATE DATABASE IF NOT EXISTS game_boosting_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    await admin_engine.dispose()

    # Create all tables
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop all tables after session
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture(autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Per-test database session with rollback for isolation."""
    async with _session_factory() as session:
        # Override the app's session dependency
        app.dependency_overrides[get_async_session] = lambda: session
        yield session
        await session.rollback()

    app.dependency_overrides.pop(get_async_session, None)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as ac:
        yield ac


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register and return a regular user with tokens."""
    resp = await client.post("/auth/register", json={
        "email": "testuser@example.com",
        "username": "TestUser",
        "password": "TestPass123",
    })
    assert resp.status_code in (200, 201)
    return resp.json()


@pytest.fixture
async def booster_user(client: AsyncClient, db_session: AsyncSession) -> dict:
    """Register a user then promote to BOOSTER via DB."""
    resp = await client.post("/auth/register", json={
        "email": "booster@example.com",
        "username": "TestBooster",
        "password": "BoostPass123",
    })
    assert resp.status_code in (200, 201)
    data = resp.json()

    # Promote to booster
    from app.models.user import User, UserRole
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.email == "booster@example.com"))
    user = result.scalar_one()
    user.role = UserRole.BOOSTER
    await db_session.flush()

    # Re-login to get token with updated role
    login_resp = await client.post("/auth/login", json={
        "email": "booster@example.com",
        "password": "BoostPass123",
    })
    assert login_resp.status_code == 200
    return login_resp.json()


@pytest.fixture
async def admin_user(client: AsyncClient, db_session: AsyncSession) -> dict:
    """Register a user then promote to ADMIN via DB."""
    resp = await client.post("/auth/register", json={
        "email": "admin_test@example.com",
        "username": "TestAdmin",
        "password": "AdminPass123",
    })
    assert resp.status_code in (200, 201)

    from app.models.user import User, UserRole
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.email == "admin_test@example.com"))
    user = result.scalar_one()
    user.role = UserRole.ADMIN
    await db_session.flush()

    login_resp = await client.post("/auth/login", json={
        "email": "admin_test@example.com",
        "password": "AdminPass123",
    })
    assert login_resp.status_code == 200
    return login_resp.json()


def auth_header(user_data: dict) -> dict:
    """Build Authorization header from login/register response."""
    return {"Authorization": f"Bearer {user_data['access_token']}"}
