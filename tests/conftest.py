from operator import attrgetter
import shutil
import tempfile

from simplekv.fs import FilesystemStore
from simplekv.memory import DictStore

import pytest


def dict_store(stores_config):
    yield DictStore()


def filesystem_store(stores_config):
    tmpdir = tempfile.mkdtemp()
    yield FilesystemStore(tmpdir)
    shutil.rmtree(tmpdir)


# all stores that support the basic interface
store_funcs = [
    dict_store,
    filesystem_store,
]


# all stores that support the url interface
urlstore_funcs = [
    filesystem_store,
]


@pytest.fixture
def stores_config():
    return {}


# it would be oh-so-nice if parameters could be fixtures again
# however, that doesn't seem to be possible, so we pass in a shared
# stores config to allow module level fixtures
@pytest.yield_fixture(params=store_funcs,
                      ids=map(attrgetter('__name__'), store_funcs))
def store(request, stores_config):
    store = request.param(stores_config)

    val = store.next()
    yield val

    store.next()  # finish up, raising StopIteration


@pytest.yield_fixture(params=urlstore_funcs,
                      ids=map(attrgetter('__name__'), urlstore_funcs))
def urlstore(request, stores_config):
    store = request.param(stores_config)

    val = store.next()
    yield val

    store.next()  # finish up, raising StopIteration)
