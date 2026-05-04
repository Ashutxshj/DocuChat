from __future__ import annotations

import json
from collections import defaultdict, deque
from datetime import datetime, timezone
from logging import getLogger

from redis.asyncio import Redis

from app.models.schemas import ChatHistoryMessage
from app.utils.config import get_settings

logger = getLogger(__name__)


class ChatMemoryService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.window = self.settings.chat_memory_window
        self.redis = Redis.from_url(self.settings.redis_url, decode_responses=True) if self.settings.redis_url else None
        self.memory: dict[str, deque[dict[str, str]]] = defaultdict(lambda: deque(maxlen=self.window))

    def _memory_key(self, user_id: str, session_id: str) -> str:
        return f"{user_id}:{session_id}"

    async def append_message(self, user_id: str, session_id: str, role: str, content: str) -> None:
        item = {
            "role": role,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        key = self._memory_key(user_id, session_id)

        if self.redis:
            try:
                await self.redis.rpush(key, json.dumps(item))
                await self.redis.ltrim(key, -self.window, -1)
                return
            except Exception:
                logger.warning("Redis unavailable, falling back to in-memory chat memory")

        self.memory[key].append(item)

    async def get_history(self, user_id: str, session_id: str, limit: int | None = None) -> list[ChatHistoryMessage]:
        key = self._memory_key(user_id, session_id)
        data: list[dict[str, str]]

        if self.redis:
            try:
                raw_items = await self.redis.lrange(key, 0, -1)
                data = [json.loads(item) for item in raw_items]
            except Exception:
                logger.warning("Redis unavailable while reading history, using in-memory chat memory")
                data = list(self.memory[key])
        else:
            data = list(self.memory[key])

        if limit is not None:
            data = data[-limit:]

        return [ChatHistoryMessage(**item) for item in data]


chat_memory_service = ChatMemoryService()
