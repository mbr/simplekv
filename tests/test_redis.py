#!/usr/bin/env python

from basic_store import BasicStore

import pytest


@pytest.fixture(scope='module')
def redis_mod():
    try:
        import redis
    except ImportError:
        pytest.skip('redis package is not installed.')

    return redis


@pytest.yield_fixture()
def redis_con(redis_mod):
    from redis.exceptions import ConnectionError

    # no configuration, for now
    con = redis_mod.StrictRedis()

    try:
        con.get('anything')
    except ConnectionError:
        pytest.skip('Could not connect to redis server')

    con.flushdb()
    yield con
    con.flushdb()


class TestRedisStore(BasicStore):
    @pytest.fixture()
    def store(self, redis_con):
        from simplekv.memory.redisstore import RedisStore
        return RedisStore(redis_con)
