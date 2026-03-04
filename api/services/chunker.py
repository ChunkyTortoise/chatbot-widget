from api.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    # Split on sentence boundaries where possible
    sentences = _split_sentences(text)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) > chunk_size and current:
            chunks.append(current.strip())
            # Start new chunk with overlap
            words = current.split()
            overlap_text = " ".join(words[-overlap:]) if len(words) > overlap else current
            current = overlap_text + " " + sentence
        else:
            current += (" " if current else "") + sentence

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if c]


def _split_sentences(text: str) -> list[str]:
    import re
    # Split on sentence-ending punctuation followed by whitespace
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if p.strip()]
