#!/usr/bin/env python

from basic_store import BasicStore, TTLStore
from simplekv import CopyMoveMixin

import pytest
redis = pytest.importorskip('redis')

from redis import StrictRedis
from redis.exceptions import ConnectionError


class TestRedisStore(TTLStore, BasicStore):
    @pytest.yield_fixture()
    def store(self):
        from simplekv.memory.redisstore import RedisStore
        r = StrictRedis()

        try:
            r.get('anything')
        except ConnectionError:
            pytest.skip('Could not connect to redis server')

        r.flushdb()
        yield RedisStore(r)
        r.flushdb()

    @pytest.yield_fixture()
    def copy_move_store(self):
        from simplekv.memory.redisstore import RedisStore

        class CopyMoveStore(RedisStore, CopyMoveMixin):
            pass

        r = StrictRedis()

        try:
            r.get('anything')
        except ConnectionError:
            pytest.skip('Could not connect to redis server')

        r.flushdb()
        yield CopyMoveStore(r)
        r.flushdb()
