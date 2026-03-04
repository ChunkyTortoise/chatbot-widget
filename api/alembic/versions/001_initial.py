"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-03
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "chatbots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("system_prompt", sa.Text, nullable=False),
        sa.Column("welcome_message", sa.String(500), default="Hi! How can I help you today?"),
        sa.Column("primary_color", sa.String(7), default="#3B82F6"),
        sa.Column("position", sa.String(20), default="bottom-right"),
        sa.Column("title", sa.String(100), default="Chat with us"),
        sa.Column("api_key_hash", sa.String(200), nullable=False),
        sa.Column("owner_email", sa.String(200)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "knowledge_docs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("chatbot_id", UUID(as_uuid=True), sa.ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("content_text", sa.Text, nullable=False),
        sa.Column("chunk_count", sa.Integer, default=0),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("error_message", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_docs_chatbot_id", "knowledge_docs", ["chatbot_id"])

    op.create_table(
        "document_chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("doc_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_docs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chatbot_id", UUID(as_uuid=True), sa.ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_chunks_chatbot_id", "document_chunks", ["chatbot_id"])

    op.create_table(
        "conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("chatbot_id", UUID(as_uuid=True), sa.ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_id", sa.String(100), nullable=False),
        sa.Column("message_count", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_conversations_session", "conversations", ["session_id"])

    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_messages_conversation", "messages", ["conversation_id"])


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("document_chunks")
    op.drop_table("knowledge_docs")
    op.drop_table("chatbots")
