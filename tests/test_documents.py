import pytest
import uuid
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_upload_document_requires_admin_key(client, chatbot_id):
    content = b"Test document content"
    response = await client.post(
        f"/api/v1/chatbots/{chatbot_id}/documents",
        files={"file": ("test.txt", BytesIO(content), "text/plain")},
    )
    assert response.status_code == 422  # Missing admin key


@pytest.mark.asyncio
async def test_upload_invalid_file_type(client, admin_headers, chatbot_id):
    with patch("api.routes.documents.get_db"), \
         patch("api.routes.documents.get_admin_key", return_value="dev-admin-key"):
        response = await client.post(
            f"/api/v1/chatbots/{chatbot_id}/documents",
            files={"file": ("test.doc", BytesIO(b"content"), "application/msword")},
            headers=admin_headers,
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_file_too_large(client, admin_headers, chatbot_id):
    with patch("api.routes.documents.get_db"), \
         patch("api.routes.documents.get_admin_key", return_value="dev-admin-key"):
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        response = await client.post(
            f"/api/v1/chatbots/{chatbot_id}/documents",
            files={"file": ("big.txt", BytesIO(large_content), "text/plain")},
            headers=admin_headers,
        )
        assert response.status_code == 413


@pytest.mark.asyncio
async def test_list_documents_requires_admin_key(client, chatbot_id):
    response = await client.get(f"/api/v1/chatbots/{chatbot_id}/documents")
    assert response.status_code == 422


def test_extract_text_from_txt():
    """Test text extraction from plain text files."""
    from api.routes.documents import _extract_text
    content = b"Hello, world!\nSecond line."
    result = _extract_text(content, "test.txt")
    assert "Hello" in result
    assert "Second line" in result


def test_extract_text_preserves_content():
    """Text extraction should preserve all content."""
    from api.routes.documents import _extract_text
    text = "Important content here. More content. Final sentence."
    result = _extract_text(text.encode(), "document.txt")
    assert result == text
