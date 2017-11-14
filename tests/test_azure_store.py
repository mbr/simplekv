from uuid import uuid4 as uuid
from simplekv._compat import ConfigParser, pickle
from simplekv.net.azurestore import AzureBlockBlobStore
from simplekv.contrib import ExtendedKeyspaceMixin
from basic_store import BasicStore
from conftest import ExtendedKeyspaceTests
import pytest

pytest.importorskip('azure.storage')


def load_azure_credentials():
    # loaded from the same place as tox.ini. here's a sample
    #
    # [my-azure-storage-account]
    # account_name=foo
    # account_key=bar
    cfg_fn = 'azure_credentials.ini'

    parser = ConfigParser()
    result = parser.read(cfg_fn)
    if not result:
        pytest.skip('file {} not found'.format(cfg_fn))

    for section in parser.sections():
        return {
            'account_name': parser.get(section, 'account_name'),
            'account_key': parser.get(section, 'account_key'),
        }


def create_azure_conn_string(credentials):
    account_name = credentials['account_name']
    account_key = credentials['account_key']
    fmt_str = 'DefaultEndpointsProtocol=https;AccountName={};AccountKey={}'
    return fmt_str.format(account_name, account_key)


class TestAzureStorage(BasicStore):
    @pytest.fixture
    def store(self):
        from azure.storage.blob import BlockBlobService

        container = uuid()
        conn_string = create_azure_conn_string(load_azure_credentials())
        s = BlockBlobService(connection_string=conn_string)

        yield AzureBlockBlobStore(conn_string=conn_string, container=container,
                                  public=False)
        s.delete_container(container)

    def test_open_seek_and_tell(self, store, key, long_value):
        store.put(key, long_value)
        ok = store.open(key)
        ok.seek(10)
        assert ok.tell() == 10
        ok.seek(-6, 1)
        assert ok.tell() == 4
        with pytest.raises(IOError):
            ok.seek(-1, 0)
        with pytest.raises(IOError):
            ok.seek(-6, 1)
        with pytest.raises(IOError):
            ok.seek(-len(long_value) - 1, 2)

        assert ok.tell() == 4
        assert long_value[4:5] == ok.read(1)
        assert ok.tell() == 5
        ok.seek(-1, 2)
        length_lv = len(long_value)
        assert long_value[length_lv - 1:length_lv] == ok.read(1)
        assert ok.tell() == length_lv


class TestExtendedKeysAzureStorage(TestAzureStorage, ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self):
        class ExtendedKeysStore(ExtendedKeyspaceMixin, AzureBlockBlobStore):
            pass
        from azure.storage.blob import BlockBlobService

        container = uuid()
        conn_string = create_azure_conn_string(load_azure_credentials())
        s = BlockBlobService(connection_string=conn_string)

        yield ExtendedKeysStore(conn_string=conn_string,
                                container=container, public=False)
        s.delete_container(container)


def test_azure_setgetstate():
    from azure.storage.blob import BlockBlobService
    container = uuid()
    conn_string = create_azure_conn_string(load_azure_credentials())
    s = BlockBlobService(connection_string=conn_string)
    store = AzureBlockBlobStore(conn_string=conn_string, container=container,
                                public=False)
    store.put(u'key1', b'value1')

    buf = pickle.dumps(store, protocol=2)
    store = pickle.loads(buf)

    assert store.get(u'key1') == b'value1'
    s.delete_container(container)
