from unittest import mock
from simplekv import KeyValueStore

def test_keyvaluestore_enter_exit():
    with mock.patch("simplekv.KeyValueStore.close") as closefunc:
        with KeyValueStore() as kv:
            pass
        closefunc.assert_called_once()
