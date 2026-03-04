import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client, mock_db, mock_redis):
    from sqlalchemy import text
    mock_db.execute = pytest.importorskip  # will be called
    mock_db.execute = __import__("unittest.mock", fromlist=["AsyncMock"]).AsyncMock()

    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db_ok" in data
    assert "redis_ok" in data


@pytest.mark.asyncio
async def test_health_returns_dict(client):
    response = await client.get("/health")
    data = response.json()
    assert isinstance(data, dict)
    assert set(data.keys()) >= {"status", "db_ok", "redis_ok"}


@pytest.mark.asyncio
async def test_health_status_field_exists(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ("healthy", "degraded")
