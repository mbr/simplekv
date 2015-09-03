import random
import string
from simplekv._compat import BytesIO, xrange
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

    @pytest.fixture
    def store(self, prefix):
        def randstring():
            return u''.join(random.choice(string.ascii_lowercase)
                            for _ in xrange(8))

        base_store = DictStore()
        base_store.put(randstring(), randstring().encode('utf8'))
        base_store.put(randstring(), randstring().encode('utf8'))
        base_store.put(randstring(), randstring().encode('utf8'))

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
