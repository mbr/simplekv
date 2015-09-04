from simplekv._compat import BytesIO
from simplekv.memory import DictStore
from simplekv.decorator import PrefixDecorator
import pytest

from basic_store import BasicStore


class TestPrefixDecorator(BasicStore):
    @pytest.fixture(params=[
        'short_',
        'loooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_',
        'nounderscore',
        '_129073ashd812g',
    ])
    def prefix(self, request):
        return request.param

    @pytest.fixture(params=['prefix2_', 'zz', ])
    def prefix2(self, request):
        # these are used when multiple prefixes in a single store
        # are requested
        return request.param

    @pytest.fixture(params=[True, False])
    def store(self, request, prefix):
        base_store = DictStore()

        # do we add extra keys to the underlying store?
        if request.param:
            base_store.put('some_other_value', b'data1')
            base_store.put('ends_with_short_', b'data2')
            base_store.put('xx', b'data3')
            base_store.put('test', b'data4')

        return PrefixDecorator(prefix, base_store)

    def test_put_returns_correct_key(self, store, prefix, key, value):
        assert key == store.put(key, value)

    def test_put_sets_prefix(self, store, prefix, key, value):
        full_key = prefix + key
        key == store.put(key, value)

        assert store._dstore.get(full_key) == value

    def test_put_file_returns_correct_key(self, store, prefix, key, value):
        assert key == store.put_file(key, BytesIO(value))

    def test_put_file_sets_prefix(self, store, prefix, key, value):
        full_key = prefix + key
        key == store.put_file(key, BytesIO(value))

        assert store._dstore.get(full_key) == value

    def test_multiple_prefixes_one_store(self, store, prefix, prefix2, key,
                                         value):
        base_store = store._dstore
        store2 = PrefixDecorator(prefix2, base_store)

        pv = value + prefix.encode('ascii')
        pv2 = value + prefix2.encode('ascii')

        # put in with each prefix
        store.put(key, pv)
        store2.put(key, pv2)

        assert key in store
        assert key in store2

        assert prefix + key in base_store
        assert prefix2 + key in base_store

        assert len(store.keys()) == 1
        assert len(store2.keys()) == 1

        assert store.get(key) == pv
        assert store2.get(key) == pv2
