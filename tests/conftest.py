import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_embed():
    """Returns a fixed 384-dim vector."""
    with patch("api.services.embedder.embed") as m:
        m.return_value = [0.1] * 384
        yield m


@pytest.fixture
def mock_embed_batch():
    """Returns fixed 384-dim vectors for a batch."""
    with patch("api.services.embedder.embed_batch") as m:
        m.side_effect = lambda texts: [[0.1] * 384 for _ in texts]
        yield m


@pytest.fixture
def mock_anthropic():
    """Mock Claude streaming responses."""
    with patch("api.services.chat_service.anthropic.AsyncAnthropic") as m:
        client = AsyncMock()
        m.return_value = client

        stream = AsyncMock()
        stream.__aenter__ = AsyncMock(return_value=stream)
        stream.__aexit__ = AsyncMock(return_value=False)

        async def token_gen():
            for token in ["Hello", " ", "world", "!"]:
                yield token

        stream.text_stream = token_gen()
        client.messages.stream.return_value = stream
        yield client


@pytest.fixture
def mock_db():
    """Async mock DB session with properly configured execute return value."""
    session = AsyncMock()
    # Return a regular MagicMock so sync methods (scalar_one_or_none, scalars) work
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    result.scalar_one.return_value = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result
    return session


@pytest.fixture
def mock_redis():
    """Async mock Redis client."""
    r = AsyncMock()
    r.ping = AsyncMock()
    return r


@pytest.fixture
async def client(mock_db, mock_redis):
    """Test client with dependency overrides for DB and Redis."""
    from httpx import AsyncClient, ASGITransport
    from api.main import app
    from api.dependencies import get_db, get_redis

    async def override_get_db():
        yield mock_db

    async def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers():
    return {"X-Admin-Key": "dev-admin-key"}


@pytest.fixture
def chatbot_id():
    return str(uuid.uuid4())
