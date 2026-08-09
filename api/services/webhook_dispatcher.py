"""Best-effort internal event dispatcher.

Webhook subscription delivery is not configured in this application yet.  The
chat flow still emits lifecycle events so a later delivery integration has one
stable call site, while local and CI runs remain deterministic.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def dispatch_event(
    *, chatbot_id: UUID, event_type: str, data: dict[str, Any], db: AsyncSession
) -> None:
    """Record a lifecycle event until outbound webhook subscriptions are added."""
    del db
    logger.info(
        "Webhook delivery is not configured: chatbot_id=%s event_type=%s payload_keys=%s",
        chatbot_id,
        event_type,
        sorted(data),
    )
