from uuid import uuid4 as uuid
from simplekv._compat import ConfigParser, pickle
from simplekv.net.azurestore import AzureBlockBlobStore
from simplekv.contrib import ExtendedKeyspaceMixin
from basic_store import BasicStore, OpenSeekTellStore
from conftest import ExtendedKeyspaceTests
import pytest

pytest.importorskip('azure.storage.blob')


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


class TestAzureStorage(BasicStore, OpenSeekTellStore):
    @pytest.fixture
    def store(self):
        from azure.storage.blob import BlockBlobService

        container = uuid()
        conn_string = create_azure_conn_string(load_azure_credentials())
        s = BlockBlobService(connection_string=conn_string)

        yield AzureBlockBlobStore(conn_string=conn_string, container=container,
                                  public=False)
        s.delete_container(container)


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
    store = AzureBlockBlobStore(conn_string=conn_string, container=container)
    store.put(u'key1', b'value1')

    buf = pickle.dumps(store, protocol=2)
    store = pickle.loads(buf)

    assert store.get(u'key1') == b'value1'
    s.delete_container(container)


class TestAzureExceptionHandling(object):
    def test_missing_container(self):
        container = uuid()
        conn_string = create_azure_conn_string(load_azure_credentials())
        store = AzureBlockBlobStore(conn_string=conn_string,
                                    container=container,
                                    create_if_missing=False)
        with pytest.raises(IOError) as exc:
            store.iter_keys()
        assert u"The specified container does not exist." in str(exc.value)

    def test_wrong_endpoint(self):
        from azure.storage.common.retry import ExponentialRetry
        container = uuid()
        conn_string = create_azure_conn_string(load_azure_credentials())
        conn_string += \
            ";BlobEndpoint=https://hopenostorethere.blob.core.windows.net;"
        store = AzureBlockBlobStore(conn_string=conn_string,
                                    container=container,
                                    create_if_missing=False)
        store.block_blob_service.retry = ExponentialRetry(max_attempts=0).retry

        with pytest.raises(IOError) as exc:
            store.put(u"key", b"data")
        assert u"Failed to establish a new connection" in str(exc.value)

    def test_wrong_credentials(self):
        from azure.storage.common.retry import ExponentialRetry
        container = uuid()
        conn_string = \
            'DefaultEndpointsProtocol=https;AccountName={};AccountKey={}'.\
            format("testaccount", "wrongsecret")
        store = AzureBlockBlobStore(conn_string=conn_string,
                                    container=container,
                                    create_if_missing=False)
        store.block_blob_service.retry = ExponentialRetry(max_attempts=0).retry

        with pytest.raises(IOError) as exc:
            store.put(u"key", b"data")
        assert u"Incorrect padding" in str(exc.value)
