from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class KnowledgeDoc(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "knowledge_docs"

    chatbot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chatbots.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending/processed/failed
    error_message: Mapped[str | None] = mapped_column(Text)

    chatbot: Mapped["Chatbot"] = relationship(back_populates="knowledge_docs")
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="doc", cascade="all, delete-orphan"
    )
