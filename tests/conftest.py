import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE_URL = "http://test"

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=BASE_URL
    ) as ac:
        yield ac