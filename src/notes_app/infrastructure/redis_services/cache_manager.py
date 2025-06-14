from typing import cast, Any, Union, Optional, AsyncIterator, Iterator
from notes_app.infrastructure.redis_services.redis_client import AsyncRedis, SyncRedis
import json
from notes_app.infrastructure.config import config


class CacheManager:
    def __init__(self, redis_client: Union[AsyncRedis, SyncRedis]):
        self.client = redis_client

    @staticmethod
    async def generate_key(*args) -> str:
        return ":".join(str(arg) for arg in args)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> None:
        ex = ex or config.REDIS_CACHE_EXPIRE_SECONDS
        await self.client.set(key, json.dumps(value), ex=ex)

    async def get(self, key: str) -> Any:
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def delete(self, *keys: str) -> None:
        await self.client.delete(*keys)

    async def delete_pattern(self, pattern: str) -> None:
        keys = []
        async_iter = cast(AsyncIterator, self.client.scan_iter(match=pattern))
        async for key in async_iter:
            keys.append(key)
        if keys:
            await self.client.delete(*keys)

    def sync_delete_pattern(self, pattern: str) -> None:
        keys = []
        sync_iter = cast(Iterator, self.client.scan_iter(match=pattern))
        for key in sync_iter:
            keys.append(key)
        if keys:
            self.client.delete(*keys)
