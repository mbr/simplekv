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


def test_context_manager_deletes_bucket(credentials):
    with boto_bucket(access_key=credentials['access_key'],
                     secret_key=credentials['secret_key'],
                     connect_func=credentials['connect_func']) as bucket:
        k = Key(bucket)
        k.key = 'test_key'
        k.set_contents_from_string('asdf')
        bucket_name = bucket.name

    # check if the bucket was deleted
    conn = getattr(boto, credentials['connect_func'])(
        credentials['access_key'], credentials['secret_key']
    )

    try:
        conn.get_bucket(bucket_name)
    except StorageResponseError as e:
        assert e.code == 'NoSuchBucket'
    else:
        assert False, 'bucket not deleted'
