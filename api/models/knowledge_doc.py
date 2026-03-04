import uuid
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, UUIDMixin, TimestampMixin


class KnowledgeDoc(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "knowledge_docs"

    chatbot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/processed/failed
    error_message: Mapped[str | None] = mapped_column(Text)

    chatbot: Mapped["Chatbot"] = relationship(back_populates="knowledge_docs")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="doc", cascade="all, delete-orphan")
