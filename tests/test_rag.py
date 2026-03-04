import pytest
from unittest.mock import patch, MagicMock


class TestChunker:
    def test_basic_chunking(self):
        from api.services.chunker import chunk_text
        text = "Hello world. " * 50  # ~650 chars
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        assert len(chunks) > 1
        assert all(isinstance(c, str) for c in chunks)
        assert all(c.strip() for c in chunks)

    def test_short_text_single_chunk(self):
        from api.services.chunker import chunk_text
        text = "Short text."
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunks_contain_original_content(self):
        from api.services.chunker import chunk_text
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunk_text(text, chunk_size=40, overlap=10)
        combined = " ".join(chunks)
        # Key words should appear somewhere
        assert "First" in combined
        assert "Fourth" in combined

    def test_empty_text(self):
        from api.services.chunker import chunk_text
        chunks = chunk_text("", chunk_size=400, overlap=50)
        assert chunks == []

    def test_chunk_size_respected(self):
        from api.services.chunker import chunk_text
        text = "Word. " * 200  # ~1200 chars
        chunks = chunk_text(text, chunk_size=200, overlap=20)
        # Most chunks should be close to chunk_size
        for chunk in chunks[:-1]:  # last chunk can be short
            assert len(chunk) <= 300  # allow some overage from sentence boundaries

    def test_returns_list_of_strings(self):
        from api.services.chunker import chunk_text
        result = chunk_text("Some text here.")
        assert isinstance(result, list)


class TestEmbedder:
    def test_embed_returns_list_of_floats(self):
        with patch("api.services.embedder._get_model") as mock_model:
            import numpy as np
            mock_instance = MagicMock()
            mock_instance.encode.return_value = np.array([0.1] * 384)
            mock_model.return_value = mock_instance

            from api.services.embedder import embed
            result = embed("test text")
            assert isinstance(result, list)
            assert len(result) == 384
            assert all(isinstance(v, float) for v in result)

    def test_embed_batch_returns_correct_count(self):
        with patch("api.services.embedder._get_model") as mock_model:
            import numpy as np
            mock_instance = MagicMock()
            mock_instance.encode.return_value = np.array([[0.1] * 384, [0.2] * 384, [0.3] * 384])
            mock_model.return_value = mock_instance

            from api.services.embedder import embed_batch
            result = embed_batch(["a", "b", "c"])
            assert len(result) == 3
            assert all(len(v) == 384 for v in result)

    def test_embed_truncates_long_text(self):
        with patch("api.services.embedder._get_model") as mock_model:
            import numpy as np
            mock_instance = MagicMock()
            mock_instance.encode.return_value = np.array([0.1] * 384)
            mock_model.return_value = mock_instance

            from api.services.embedder import embed, MAX_CHARS
            long_text = "x" * (MAX_CHARS + 1000)
            embed(long_text)

            # Verify the text was truncated before being passed to encode
            call_args = mock_instance.encode.call_args
            passed_text = call_args[0][0]
            assert len(passed_text) <= MAX_CHARS
