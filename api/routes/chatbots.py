import uuid
import secrets
import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from api.dependencies import get_db, get_admin_key
from api.models.chatbot import Chatbot
from api.schemas.chatbot import (
    ChatbotCreate,
    ChatbotUpdate,
    ChatbotResponse,
    CreateChatbotResponse,
    WidgetConfig,
)
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)


def _hash_api_key(raw_key: str) -> str:
    """SHA-256 hash for randomly-generated API keys (not passwords)."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def _verify_api_key(raw_key: str, stored_hash: str) -> bool:
    return hashlib.sha256(raw_key.encode()).hexdigest() == stored_hash


@router.post("/chatbots", response_model=CreateChatbotResponse)
async def create_chatbot(
    payload: ChatbotCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_admin_key),
):
    raw_key = f"cbk_{secrets.token_urlsafe(32)}"
    hashed = _hash_api_key(raw_key)

    chatbot = Chatbot(
        id=uuid.uuid4(),
        name=payload.name,
        system_prompt=payload.system_prompt,
        welcome_message=payload.welcome_message,
        primary_color=payload.primary_color,
        position=payload.position,
        title=payload.title,
        owner_email=payload.owner_email,
        api_key_hash=hashed,
        created_at=datetime.now(timezone.utc),
    )
    db.add(chatbot)
    await db.commit()
    await db.refresh(chatbot)

    return CreateChatbotResponse(
        id=chatbot.id,
        name=chatbot.name,
        system_prompt=chatbot.system_prompt,
        welcome_message=chatbot.welcome_message,
        primary_color=chatbot.primary_color,
        position=chatbot.position,
        title=chatbot.title,
        owner_email=chatbot.owner_email,
        is_active=chatbot.is_active,
        api_key=raw_key,
    )


@router.get("/chatbots/{chatbot_id}", response_model=ChatbotResponse)
async def get_chatbot(
    chatbot_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_admin_key),
):
    result = await db.execute(select(Chatbot).where(Chatbot.id == chatbot_id))
    chatbot = result.scalar_one_or_none()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Not found")
    return chatbot


@router.get("/chatbots/{chatbot_id}/widget-config", response_model=WidgetConfig)
async def get_widget_config(
    chatbot_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — returns display config only, no sensitive data."""
    result = await db.execute(
        select(Chatbot).where(Chatbot.id == chatbot_id, Chatbot.is_active == True)
    )
    chatbot = result.scalar_one_or_none()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Not found")
    return WidgetConfig(
        id=chatbot.id,
        name=chatbot.name,
        welcome_message=chatbot.welcome_message,
        primary_color=chatbot.primary_color,
        position=chatbot.position,
        title=chatbot.title,
    )


@router.put("/chatbots/{chatbot_id}", response_model=ChatbotResponse)
async def update_chatbot(
    chatbot_id: uuid.UUID,
    payload: ChatbotUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_admin_key),
):
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    await db.execute(update(Chatbot).where(Chatbot.id == chatbot_id).values(**updates))
    await db.commit()

    result = await db.execute(select(Chatbot).where(Chatbot.id == chatbot_id))
    return result.scalar_one()


@router.delete("/chatbots/{chatbot_id}", status_code=204)
async def delete_chatbot(
    chatbot_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_admin_key),
):
    await db.execute(
        update(Chatbot).where(Chatbot.id == chatbot_id).values(is_active=False)
    )
    await db.commit()
