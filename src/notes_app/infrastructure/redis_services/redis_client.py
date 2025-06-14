from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis
from notes_app.infrastructure.config import config


async_redis_client = AsyncRedis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)

sync_redis_client = SyncRedis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)
