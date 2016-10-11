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
    # [my-azure-storage-account]
    # account_name=foo
    # account_key=bar
    cfg_fn = 'azure_credentials.ini'

    parser = ConfigParser()
    if not parser.read(cfg_fn):
        pytest.skip('file {} not found'.format(cfg_fn))

    for section in parser.sections():
        return {
            'account_name': parser.get(section, 'account_name'),
            'account_key': parser.get(section, 'account_key'),
        }

def create_azure_account(credentials):
    account_name = credentials['account_name']
    account_key = credentials['account_key']
    return CloudStorageAccount(account_name=account_name, account_key=account_key) 

class TestAzureStorage(BasicStore, UrlStore):
    @pytest.fixture(params=['', '/test-prefix'])
    def prefix(self, request):
        return request.param

    # @pytest.fixture(params='testrun-bucket-{}'.format(uuid()))
    @pytest.fixture(params=[uuid()])
    def container(self, request):
        return request.param

    @pytest.fixture
    def store(self, container, prefix):
        account = create_azure_account(load_azure_credentials())
        return AzureBlockBlobStorage(account, container, prefix=prefix, public=False)
