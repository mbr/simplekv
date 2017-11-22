# coding=utf-8
from simplekv.transform import Gzip, ValueTransformingDecorator
from simplekv.memory import DictStore
import pytest
import tempfile
from util import ReverseTransformerPair


@pytest.fixture()
def store():
    return DictStore()


def test_str(store):
    decorated = ValueTransformingDecorator(store, [Gzip()])
    assert str(decorated) == 'ValueTrafo({}, Gzip)'.format(store)
    decorated = ValueTransformingDecorator(store, [Gzip(), Gzip()])
    assert str(decorated) == 'ValueTrafo({}, Gzip | Gzip)'.format(store)


def test_put_get(store, value):
    store = ValueTransformingDecorator(store, [Gzip()])
    key = u'key0'
    store.put(key, value)
    # check that some transformation happened:
    assert store._dstore.get(key) != value
    assert store.get(key) == value


def test_put_get_file(store, value):
    store = ValueTransformingDecorator(store, [Gzip()])
    key = u'key0'
    with tempfile.NamedTemporaryFile('wb+', 0) as file:
        file.write(value)
        store.put_file(key, file.name)
    with tempfile.NamedTemporaryFile('wb+', 0) as file:
        store.get_file(key, file.name)
        assert file.read() == value


def test_open(store, value):
    store = ValueTransformingDecorator(store, [Gzip()])
    key = u'key0'
    store.put(key, value)
    f = store.open(key)
    assert f.read() == value


def test_forwards(store, value):
    store = ValueTransformingDecorator(store, [Gzip()])
    key = u'key0'
    store.put(key, value)
    assert list(store) == [key]
    assert key in store
    assert list(store.iter_keys()) == [key]
    store.delete(key)
    assert list(store) == []
    with pytest.raises(AttributeError):
        store.url_for


def test_gzip_reverse(store, value):
    store = ValueTransformingDecorator(
        store, [Gzip(), ReverseTransformerPair()]
    )
    key = u'key0'
    store.put(key, value)
    assert store.get(key) == value
    assert store.open(key).read() == value
