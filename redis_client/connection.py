from asyncio import Lock

import redis.asyncio as redis

from config import settings


class RedisConnection:
    """
    Redis connection manager implementing a thread-safe singleton pattern.

    This class maintains a single Redis connection pool across the application
    using a double-checked locking pattern to ensure thread safety in async contexts.

    Attributes:
        _pool: Redis connection pool instance shared across all instances
        _lock: Asyncio lock for thread-safe pool initialization
    """
    _pool = None
    _lock = Lock()

    @classmethod
    async def get_pool(cls):
        """
        Get or create a Redis connection pool.

        This method uses double-checked locking to ensure the connection pool
        is initialized only once, even in concurrent async environments.

        Returns:
            Redis connection pool configured with settings from config.
        """
        if cls._pool is None:
            async with cls._lock:
                if cls._pool is None:  # Double-check after acquiring lock
                    redis_url = settings.REDIS_URL
                    cls._pool = await redis.from_url(
                        redis_url,
                        encoding="utf8",
                        decode_responses=True
                    )
        return cls._pool
