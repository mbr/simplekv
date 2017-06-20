from uuid import uuid4 as uuid
from simplekv._compat import ConfigParser, pickle
from simplekv.net.azurestore import AzureBlockBlobStore
from basic_store import BasicStore
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
    print(result)
    print(type(result))
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
