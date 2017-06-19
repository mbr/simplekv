from simplekv.memory import DictStore
from simplekv.cache import CacheDecorator

from basic_store import BasicStore

import pytest


class TestCache(BasicStore):
    # FIXME: this could use some extra combinations tested
    @pytest.fixture
    def front_store(self):
        return DictStore()

    @pytest.fixture
    def backing_store(self):
        return DictStore()

    @pytest.fixture
    def store(self, front_store, backing_store):
        return CacheDecorator(front_store, backing_store)

    def test_works_when_cache_loses_key(self, store, front_store, key, value):
        store.put(key, value)

        assert store.get(key) == value

        front_store.delete(key)

        assert store.get(key) == value
