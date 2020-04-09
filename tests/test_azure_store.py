from uuid import uuid4 as uuid
from simplekv._compat import ConfigParser, pickle
from simplekv.net.azurestore import AzureBlockBlobStore
from simplekv.contrib import ExtendedKeyspaceMixin
from basic_store import BasicStore, OpenSeekTellStore
from conftest import ExtendedKeyspaceTests
import pytest
from base64 import b64encode

asb = pytest.importorskip('azure.storage.blob')


def get_azure_conn_string():
    cfg_fn = 'azure_credentials.ini'
    parser = ConfigParser()
    result = parser.read(cfg_fn)
    if not result:
        pytest.skip('file {} not found'.format(cfg_fn))

    for section in parser.sections():
        account_name = parser.get(section, 'account_name', fallback=None)
        if account_name is None:
            pytest.skip("no 'account_name' found in file {}".format(cfg_fn))

        account_key = parser.get(section, 'account_key')
        protocol = parser.get(section, 'protocol', fallback='https')
        endpoint = parser.get(section, 'endpoint', fallback=None)
        conn_string = 'DefaultEndpointsProtocol={};AccountName={};AccountKey={}'.format(
            protocol, account_name, account_key
        )
        if endpoint is not None:
            conn_string += ';BlobEndpoint={}'.format(endpoint)
        return conn_string


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
        conn_string = get_azure_conn_string()
        yield AzureBlockBlobStore(conn_string=conn_string, container=container,
                                  public=False)
        _delete_container(conn_string, container)


class TestExtendedKeysAzureStorage(TestAzureStorage, ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self):
        azure_storage_blob_major_version = int(asb.__version__.split('.', 1)[0])
        conn_string = get_azure_conn_string()
        use_azurite = 'http://127.0.0.1:10000/devstoreaccount1' in conn_string
        if use_azurite and azure_storage_blob_major_version < 12:
            pytest.skip("Compatibility issues with azurite and azure-storage-blob<12")
        container = str(uuid())

        class ExtendedKeysStore(ExtendedKeyspaceMixin, AzureBlockBlobStore):
            pass
        yield ExtendedKeysStore(conn_string=conn_string,
                                container=container, public=False)
        _delete_container(conn_string, container)


def test_azure_setgetstate():
    container = str(uuid())
    conn_string = get_azure_conn_string()
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


def test_azure_special_args():
    # For azure-storage-blob 12,
    # test that the special arguments `max_block_size` and
    # `max_single_put_size` propagate to the constructed ContainerClient
    conn_string = get_azure_conn_string()
    MBS = 983645
    MSP = 756235
    abbs = AzureBlockBlobStore(
        conn_string=conn_string,
        container='container-unused',
        max_block_size=MBS,
        max_single_put_size=MSP,
        create_if_missing=False
    )
    if hasattr(abbs, "blob_container_client"):
        cfg = abbs.blob_container_client._config
        assert cfg.max_single_put_size == MSP
        assert cfg.max_block_size == MBS


class TestAzureExceptionHandling(object):
    def test_missing_container(self):
        container = str(uuid())
        conn_string = get_azure_conn_string()
        store = AzureBlockBlobStore(conn_string=conn_string,
                                    container=container,
                                    create_if_missing=False)
        with pytest.raises(IOError) as exc:
            store.keys()
        assert u"The specified container does not exist." in str(exc.value)

    def test_wrong_endpoint(self):
        container = str(uuid())
        conn_string = get_azure_conn_string()
        conn_settings = dict([s.split("=", 1) for s in conn_string.split(";") if s])
        conn_settings['BlobEndpoint'] = 'https://host-does-not-exist/'
        conn_string = ';'.join('{}={}'.format(key, value) for key, value in conn_settings.items())
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
        conn_string = get_azure_conn_string()

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
