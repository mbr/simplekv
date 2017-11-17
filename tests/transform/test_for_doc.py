# coding=utf-8
import pytest


@pytest.fixture
def decorated_store():
    from simplekv.memory import DictStore
    return DictStore()


def test_for_doc(decorated_store):
    # test the code given as example on the 'transforms' page
    from simplekv.transform import Gzip, ValueTransformingDecorator

    store = ValueTransformingDecorator(decorated_store, Gzip())
    store.put(u'key', b'value')

    # accessing via the decorator retrieves the original value:
    assert store.get(u'key') == b'value'

    # accessing decorated_store directly will retrieve the gip'ed value:
    from gzip import GzipFile

    assert (
        GzipFile(fileobj=decorated_store.open(u'key'), mode='r').read() ==
        b'value'
    )
