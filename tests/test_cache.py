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

    def test_works_when_cache_loses_key(self, store, front_store):
        store.put('keya', 'valuea')
        store.put('keyb', 'valueb')

        assert 'valuea' == store.get('keya')
        assert 'valueb' == store.get('keyb')

        front_store.delete('keya')

        assert 'valuea' == store.get('keya')
        assert 'valueb' == store.get('keyb')
