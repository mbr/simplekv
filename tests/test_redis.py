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
        store.put(key, value, ttl=ttl)
        assert key, ttl in store

        ttl = None
        store.put(key, value, ttl=ttl)
        assert key, ttl in store

    def test_put_set_ttl(self, store, key, value):
        ttl = 604800
        store.set_ttl(ttl)
        store.put(key, value)
        assert key, ttl in store

        ttl = None
        store.set_ttl(ttl)
        store.put(key, value)
        assert key, ttl in store

    def test_put_file_with_ttl_argument(self, store, key, value):
        ttl = 604800
        store.put_file(key, BytesIO(value), ttl=ttl)
        assert key, ttl in store

    def test_put_file_set_ttl(self, store, key, value):
        ttl = 604800
        store.set_ttl(ttl)
        store.put_file(key, BytesIO(value))
        assert key, ttl in store

        ttl = None
        store.set_ttl(ttl)
        store.put_file(key, BytesIO(value))
        assert key, ttl in store
