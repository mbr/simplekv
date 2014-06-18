#!/usr/bin/env python
# coding=utf8

from simplekv.memory.memcachestore import MemcacheStore
from simplekv._compat import BytesIO

from basic_store import BasicStore

import pytest

memcache = pytest.importorskip('memcache')


class TestMemcacheStore(BasicStore):
    @pytest.yield_fixture()
    def store(self):
        mc = memcache.Client(['localhost:11211'])

        mc.set('foo', 'bar')
        if not mc.get('foo') == 'bar':
            pytest.skip('memcache connection not working')
        mc.flush_all()
        yield MemcacheStore(mc)
        mc.flush_all()

    # disabled tests (not fully API support for memcache)
    test_has_key = None
    test_has_key_with_delete = None
    test_key_iterator = None
    test_keys = None

    def test_keys_throws_io_error(self, store):
        with pytest.raises(IOError):
            store.keys()

        with pytest.raises(IOError):
            store.iter_keys()

        with pytest.raises(IOError):
            iter(store)

    def test_contains_throws_io_error_or_succeeds(self, store):
        try:
            'a' in store
        except IOError:
            pass

    def test_put_with_ttl_argument(self, store, key, value):
        ttl = 604800
        store.put(key, value, ttl=ttl)
        assert key, ttl in store

    def test_put_file_with_ttl_argument(self, store, key, value):
        ttl = 604800
        store.put_file(key, BytesIO(value), ttl=ttl)
        assert key, ttl in store
