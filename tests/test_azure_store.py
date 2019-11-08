from uuid import uuid4 as uuid
from simplekv._compat import ConfigParser, pickle
from simplekv.net.azurestore import AzureBlockBlobStore
from simplekv.contrib import ExtendedKeyspaceMixin
from basic_store import BasicStore, OpenSeekTellStore
from conftest import ExtendedKeyspaceTests
import pytest
from base64 import b64encode

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


def _delete_container(conn_string, container):
    try:
        # for azure-storage-blob>=12:
        from azure.storage.blob import BlobServiceClient
        from azure.core.exceptions import AzureError

        s = BlobServiceClient.from_connection_string(conn_string)
        try:
            s.delete_container(container)
        except AzureError as ex:
            # ignore the ContainerNotFound error:
            if ex.error_code != 'ContainerNotFound':
                raise
    except ImportError:
        # for azure-storage-blob<12
        from azure.storage.blob import BlockBlobService
        s = BlockBlobService(connection_string=conn_string)
        s.delete_container(container)


class TestAzureStorage(BasicStore, OpenSeekTellStore):
    @pytest.fixture
    def store(self):
        container = str(uuid())
        conn_string = create_azure_conn_string(load_azure_credentials())
        yield AzureBlockBlobStore(conn_string=conn_string, container=container,
                                  public=False)
        _delete_container(conn_string, container)


class TestExtendedKeysAzureStorage(TestAzureStorage, ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self):
        class ExtendedKeysStore(ExtendedKeyspaceMixin, AzureBlockBlobStore):
            pass

        container = str(uuid())
        conn_string = create_azure_conn_string(load_azure_credentials())
        yield ExtendedKeysStore(conn_string=conn_string,
                                container=container, public=False)
        _delete_container(conn_string, container)


def test_azure_setgetstate():
    container = str(uuid())
    conn_string = create_azure_conn_string(load_azure_credentials())
    store = AzureBlockBlobStore(conn_string=conn_string, container=container)
    store.put(u'key1', b'value1')

    buf = pickle.dumps(store, protocol=2)
    store = pickle.loads(buf)

    assert store.get(u'key1') == b'value1'
    _delete_container(conn_string, container)


def test_azure_store_attributes():
    abbs = AzureBlockBlobStore('CONN_STR', 'CONTAINER',
                               max_connections=42, checksum=True)
    assert abbs.conn_string == 'CONN_STR'
    assert abbs.container == 'CONTAINER'
    assert abbs.public is False
    assert abbs.create_if_missing is True
    assert abbs.max_connections == 42
    assert abbs.checksum is True

    abbs2 = pickle.loads(pickle.dumps(abbs))
    assert abbs2.conn_string == 'CONN_STR'
    assert abbs2.container == 'CONTAINER'
    assert abbs2.public is False
    assert abbs2.create_if_missing is True
    assert abbs2.max_connections == 42
    assert abbs2.checksum is True


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
        container = str(uuid())
        conn_string = create_azure_conn_string(load_azure_credentials())
        conn_string += \
            ";BlobEndpoint=https://hopenostorethere.blob.core.windows.net;"
        store = AzureBlockBlobStore(conn_string=conn_string,
                                    container=container,
                                    create_if_missing=False)
        if hasattr(store, 'block_blob_service'):
            from azure.storage.common.retry import ExponentialRetry
            store.block_blob_service.retry = ExponentialRetry(
                max_attempts=0
            ).retry
        else:
            store.blob_container_client._config.retry_policy.total_retries = 0

        with pytest.raises(IOError) as exc:
            store.put(u"key", b"data")
        assert u"connect" in str(exc.value)

    def test_wrong_credentials(self):
        container = str(uuid())
        conn_string = \
            'DefaultEndpointsProtocol=https;AccountName={};AccountKey={}'.\
            format("testaccount", "wrongsecret")
        store = AzureBlockBlobStore(conn_string=conn_string,
                                    container=container,
                                    create_if_missing=False)

        if hasattr(store, 'block_blob_service'):
            from azure.storage.common.retry import ExponentialRetry
            store.block_blob_service.retry = ExponentialRetry(
                max_attempts=0
            ).retry
        else:
            store.blob_container_client._config.retry_policy.total_retries = 0

        with pytest.raises(IOError) as exc:
            store.put(u"key", b"data")
        assert u"Incorrect padding" in str(exc.value)


class TestChecksum(object):
    CONTENT = b'\1\2\3\4'
    EXPECTED_CHECKSUM = 'CNbAWiFRKnmh3+udKo8mLw=='
    KEY = 'testkey'

    @pytest.fixture
    def store(self):
        container = str(uuid())
        conn_string = create_azure_conn_string(load_azure_credentials())

        yield AzureBlockBlobStore(
            conn_string=conn_string,
            container=container,
            public=False,
            checksum=True,
        )
        _delete_container(conn_string, container)

    def _checksum(self, store):
        # request the md5 checksum from azure and return the b64 encoded value
        if hasattr(store, 'block_blob_service'):
            return store.block_blob_service.get_blob_properties(
                store.container,
                self.KEY,
            ).properties.content_settings.content_md5
        else:
            checksum_bytes = store.blob_container_client.get_blob_client(
                self.KEY
            ).get_blob_properties().content_settings.content_md5
            return b64encode(checksum_bytes).decode()

    def test_checksum_put(self, store):
        store.put(self.KEY, self.CONTENT)
        assert self._checksum(store) == self.EXPECTED_CHECKSUM
        assert store.get(self.KEY) == self.CONTENT

    def test_checksum_put_file(self, store, tmpdir):
        file_ = tmpdir.join('my_file')
        file_.write(self.CONTENT)
        store.put_file(self.KEY, file_.open('rb'))
        assert self._checksum(store) == self.EXPECTED_CHECKSUM
        assert store.get(self.KEY) == self.CONTENT

    def test_checksum_put_filename(self, store, tmpdir):
        file_ = tmpdir.join('my_file')
        file_.write(self.CONTENT)
        store.put_file(self.KEY, str(file_))
        assert self._checksum(store) == self.EXPECTED_CHECKSUM
        assert store.get(self.KEY) == self.CONTENT
