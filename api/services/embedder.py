from functools import lru_cache
from api.config import settings

MAX_CHARS = 2000  # ~512 tokens


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


def embed(text: str) -> list[float]:
    model = _get_model()
    vector = model.encode(text[:MAX_CHARS], normalize_embeddings=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    truncated = [t[:MAX_CHARS] for t in texts]
    vectors = model.encode(truncated, normalize_embeddings=True, batch_size=32)
    return [v.tolist() for v in vectors]
