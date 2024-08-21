import asyncio
import logging

import redis.asyncio as redis
import structlog
from aiocache import caches, cached
from aiocache.backends.redis import RedisBackend, _NOT_SET
from core.settings import settings
from redis.asyncio import BlockingConnectionPool
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type, before_sleep_log

logger = structlog.get_logger('_api_')


class RedisCacheBlockingPool(RedisBackend):
    """
    Based on https://github.com/aio-libs/aiocache/pull/691
    Only use until we have this feature in package
    currently aiocache 0.12.2 NOT SUPPORT custom pool class
    """

    def __init__(self, endpoint="127.0.0.1", port=6379, db=0, password=None, pool_min_size=_NOT_SET, pool_max_size=None,
                 create_connection_timeout=None, **kwargs):
        super().__init__(endpoint, port, db, password, pool_min_size, pool_max_size, create_connection_timeout,
                         **kwargs)

        connection_pool = BlockingConnectionPool(
            host=self.endpoint, port=self.port, db=self.db,
            password=self.password, decode_responses=False,
            socket_connect_timeout=self.create_connection_timeout,
            max_connections=self.pool_max_size,
            timeout=30,  # custom
        )
        self.client = redis.Redis(connection_pool=connection_pool)

        # needed for consistency with how Redis creation of connection_pool works
        self.client.auto_close_connection_pool = True


caches.set_config({
    'default': {
        'cache': "aiocache.RedisCache",
        'namespace': settings.SERVICE_NAME,
        'serializer': {
            'class': "aiocache.serializers.PickleSerializer"
        }
    },
    'redis_alt': {
        'cache': "core.cache.RedisCacheBlockingPool",
        'endpoint': settings.REDIS_ENDPOINT,
        'namespace': settings.SERVICE_NAME,
        'port': 6379,
        'timeout': None,  # necessary for BlockingConnectionPool, because block will wait X time
        'pool_max_size': 3,  # necessary for BlockingConnectionPool, stress tests show that more than 3 is not necessary
        'serializer': {
            'class': "aiocache.serializers.PickleSerializer"
        },
        'ttl': 60 * 60 * 12  # 12 hours default value
    }
})


def key_exclude_txid(func, *args, **kwargs):
    """
    Generate a cache key for methods that use transaction_id
    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    kwargs.pop('transaction_id')
    ordered_kwargs = sorted(kwargs.items())
    return (
            (func.__module__ or "")
            + func.__name__
            + str(ordered_kwargs)
    )


class internal_cached(cached):  # noqa

    def __call__(self, f):
        self._f = f
        wrapper = super().__call__(f)
        wrapper.invalidate = self.invalidate
        return wrapper

    async def invalidate(self, *args, **kwargs):
        @retry(
            wait=wait_fixed(0.3),
            stop=stop_after_attempt(30),
            retry=(
                    retry_if_exception_type(redis.RedisError)
                    | retry_if_exception_type(asyncio.exceptions.TimeoutError)
            ),
            before_sleep=before_sleep_log(logger, logging.ERROR)
        )
        async def _wrapper():
            key = self.get_cache_key(self._f, args, kwargs)
            await self.cache.delete(key)

        await _wrapper()
