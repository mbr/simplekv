#!/usr/bin/env python

from basic_store import BasicStore

import pytest
redis = pytest.importorskip('redis')

from redis import StrictRedis
from redis.exceptions import ConnectionError

from simplekv._compat import BytesIO


class TestRedisStore(BasicStore):
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

    def test_put_with_ttl_argument(self, store, key, value):
        ttl = 604800
        store.put(key, value, ttl)
        assert ttl - 1 <= store.redis.ttl(key) <= ttl

        ttl = None
        store.put(key, value, ttl)
        assert store.redis.ttl(key) == -1

    def test_put_set_default_ttl(self, store, key, value):
        ttl = 604800
        store.set_default_ttl(ttl)
        store.put(key, value)
        assert ttl - 1 <= store.redis.ttl(key) <= ttl

        ttl = None
        store.set_default_ttl(ttl)
        store.put(key, value)
        assert store.redis.ttl(key) == -1

    def test_put_file_with_ttl_argument(self, store, key, value):
        ttl = 604800
        store.put_file(key, BytesIO(value), ttl)
        assert ttl - 1 <= store.redis.ttl(key) <= ttl

        ttl = None
        store.put_file(key, BytesIO(value), ttl)
        assert store.redis.ttl(key) == -1

    def test_put_file_set_default_ttl(self, store, key, value):
        ttl = 604800
        store.set_default_ttl(ttl)
        store.put_file(key, BytesIO(value))
        assert ttl - 1 <= store.redis.ttl(key) <= ttl

        ttl = None
        store.set_default_ttl(ttl)
        store.put_file(key, BytesIO(value))
        assert store.redis.ttl(key) == -1
