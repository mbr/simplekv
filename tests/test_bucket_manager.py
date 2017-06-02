import pytest

boto = pytest.importorskip('boto')
from boto.exception import StorageResponseError
from boto.s3.key import Key

from bucket_manager import boto_credentials, boto_bucket


@pytest.fixture(params=boto_credentials,
                ids=[c['access_key'] for c in boto_credentials])
def credentials(request):
    return request.param


@pytest.yield_fixture()
def bucket(credentials):
    with boto_bucket(**credentials) as bucket:
        yield bucket


def test_simple(bucket):
    pass


def test_simple_with_contents(bucket):
    k = bucket.new_key('i_will_prevent_deletion')
    k.set_contents_from_string('meh')
