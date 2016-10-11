from azure.storage import CloudStorageAccount
from uuid import uuid4 as uuid
import pytest

from simplekv._compat import ConfigParser
from simplekv.azure import AzureBlockBlobStorage

from basic_store import BasicStore
from url_store import UrlStore

def load_azure_credentials():
    # loaded from the same place as tox.ini. here's a sample
    #
    # [my-azure-1]
    # account_name=foo
    # account_key=bar

    # [my-azure-2]
    # account_name=bla
    # account_key=blubber
    cfg_fn = 'azure_credentials.ini'

    parser = ConfigParser()
    if not parser.read(cfg_fn):
        pytest.skip('file {} not found'.format(cfg_fn))

    # Only one entry is currently supported
    for section in parser.sections():
        yield {
            'account_name': parser.get(section, 'account_name'),
            'account_key': parser.get(section, 'account_key'),
        }

azure_credentials = list(load_azure_credentials())

def create_azure_account(credentials):
    account_name = config.STORAGE_ACCOUNT_NAME
    account_key = config.STORAGE_ACCOUNT_KEY
    return CloudStorageAccount(account_name=account_name, account_key=account_key) 

def generate_container_name():
    return 'testrun-bucket-{}'.format(uuid())

@pytest.fixture(params=azure_credentials,
                ids=[c['account_name'] for c in azure_credentials])
def credentials(request):
    return request.param

@pytest.yield_fixture()
def account(credentials):
    with azure_credentials(**credentials) as account:
        yield account

class TestAzureStorage(BasicStore, UrlStore):
    @pytest.fixture(params=['', '/test-prefix'])
    def prefix(self, request):
        return request.param

    @pytest.fixture(params='testrun-bucket-{}'.format(uuid()))
    def container(self, request):
        return request.param

    @pytest.fixture
    def store(self, container, prefix):
        account = create_azure_account(credentials)
        return AzureBlockBlobStorage(account, container, prefix=prefix, public=False)