import uuid
import hashlib
import logging
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.dependencies import get_db
from api.models.chatbot import Chatbot
from api.schemas.chat import ChatRequest, ChatResponse
from api.services.chat_service import stream_response, get_or_create_conversation

router = APIRouter()
logger = logging.getLogger(__name__)


def _verify_api_key(plain_key: str, hashed_key: str) -> bool:
    return hashlib.sha256(plain_key.encode()).hexdigest() == hashed_key


@router.post("/chat/{chatbot_id}", response_model=ChatResponse)
async def chat_rest(
    chatbot_id: uuid.UUID,
    request: ChatRequest,
    api_key: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Non-streaming REST chat endpoint."""
    result = await db.execute(select(Chatbot).where(Chatbot.id == chatbot_id, Chatbot.is_active == True))
    chatbot = result.scalar_one_or_none()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    if api_key and not _verify_api_key(api_key, chatbot.api_key_hash):
        raise HTTPException(status_code=403, detail="Invalid API key")

    full_response = ""
    async for token in stream_response(chatbot_id, request.session_id, request.message, db):
        full_response += token

    conv = await get_or_create_conversation(chatbot_id, request.session_id, db)
    return ChatResponse(
        response=full_response,
        session_id=request.session_id,
        conversation_id=str(conv.id),
    )


@router.websocket("/ws/chat/{chatbot_id}")
async def chat_websocket(
    websocket: WebSocket,
    chatbot_id: uuid.UUID,
    session_id: str = "default",
    api_key: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """WebSocket streaming chat endpoint."""
    result = await db.execute(select(Chatbot).where(Chatbot.id == chatbot_id, Chatbot.is_active == True))
    chatbot = result.scalar_one_or_none()

    if not chatbot:
        await websocket.close(code=4004)
        return

    if api_key and not _verify_api_key(api_key, chatbot.api_key_hash):
        await websocket.close(code=4003)
        return

    await websocket.accept()
    logger.info(f"WS connected: chatbot={chatbot_id} session={session_id}")

    try:
        while True:
            user_message = await websocket.receive_text()

            if user_message.strip() == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            await websocket.send_json({"type": "start"})

            try:
                async for token in stream_response(chatbot_id, session_id, user_message, db):
                    await websocket.send_json({"type": "token", "content": token})
                await websocket.send_json({"type": "end"})
            except Exception as e:
                logger.error(f"Stream error: {e}")
                await websocket.send_json({"type": "error", "content": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WS disconnected: session={session_id}")
    except Exception as e:
        logger.error(f"WS error: {e}", exc_info=True)
