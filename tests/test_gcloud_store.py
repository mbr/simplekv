import pytest

storage = pytest.importorskip("google.cloud.storage")

import os
import pickle
import time
from configparser import ConfigParser
from uuid import uuid4

import google
from basic_store import BasicStore, OpenSeekTellStore
from conftest import ExtendedKeyspaceTests
from google.auth.credentials import AnonymousCredentials
from google.cloud.exceptions import MethodNotAllowed

from simplekv.contrib import ExtendedKeyspaceMixin
from simplekv.net.gcstore import GoogleCloudStore


@pytest.fixture(scope="module")
def gc_credentials():
    parser = ConfigParser()
    parser.read("google_cloud_credentials.ini")
    credentials_path = parser.get(
        "google-cloud-tests", "credentials_json_path", fallback=None
    )
    emulator_endpoint = parser.get(
        "google-cloud-tests", "emulator_endpoint", fallback=None
    )

    assert (
        credentials_path or emulator_endpoint
    ), "Either set endpoint (for gc emulation) or credentials_json_path (for actual gc)"

    if emulator_endpoint:
        # google's client library looks for this env var
        # if we didn't set it it would use the standard endpoint
        # at https://storage.googleapis.com
        os.environ["STORAGE_EMULATOR_HOST"] = emulator_endpoint
        credentials = AnonymousCredentials()
    # if no endpoint was defined we're running against actual GC and need credentials
    else:
        # if no endpoint was defined we're running against actual GC and need credentials
        credentials = credentials_path
    yield credentials
    # unset the env var
    if emulator_endpoint:
        del os.environ["STORAGE_EMULATOR_HOST"]


def try_delete_bucket(bucket):
    # normally here we should delete the bucket
    # however the emulator (fake-gcs-server) doesn't currently support bucket deletion.
    # see: https://github.com/fsouza/fake-gcs-server/issues/214
    # So we empty the bucket and then try to delete it
    for blob in bucket.list_blobs():
        blob.delete()
    try:
        bucket.delete()
    except MethodNotAllowed as err:
        # closely match error thrown by fake gcs so we notice if something changes
        assert err.code == 405
        assert err.message.endswith("unknown error")


@pytest.fixture(scope="module")
def dirty_store(gc_credentials):
    uuid = str(uuid4())
    # if we have a credentials.json that specifies the project name, else we pick one
    if type(gc_credentials) == AnonymousCredentials:
        project_name = "testing"
    else:
        project_name = None
    store = GoogleCloudStore(
        credentials=gc_credentials, bucket_name=uuid, project=project_name
    )
    yield store
    try_delete_bucket(store._bucket)


@pytest.fixture(scope="function")
def store(dirty_store):
    for blob in dirty_store._bucket.list_blobs():
        blob.delete()

    # Google Storage doesn't like getting hit with heavy CRUD on a newly
    # create bucket. Therefore we introduce an artificial timeout
    if not os.environ.get("STORAGE_EMULATOR_HOST", None):
        time.sleep(0.2)
    return dirty_store


class TestGoogleCloudStore(OpenSeekTellStore, BasicStore):
    pass


def test_gcstore_pickling(store):
    store.put("key1", b"value1")

    buf = pickle.dumps(store)
    store = pickle.loads(buf)

    assert store.get("key1") == b"value1"


def test_gcstore_pickling_attrs():
    store = GoogleCloudStore(
        credentials="path_to_json",
        bucket_name="test_bucket",
        create_if_missing=False,
        create_bucket_location="US-CENTRAL1",
        project="sample_project",
    )

    buf = pickle.dumps(store)
    store = pickle.loads(buf)

    assert store.bucket_name == "test_bucket"
    assert not store.create_if_missing
    assert store.create_bucket_location == "US-CENTRAL1"
    assert store.project_name == "sample_project"


class TestExtendedKeysGCStore(TestGoogleCloudStore, ExtendedKeyspaceTests):
    @pytest.fixture(scope="class")
    def dirty_store(self, gc_credentials):
        uuid = str(uuid4())
        # if we have a credentials.json that specifies the project name, else we pick one
        if type(gc_credentials) == AnonymousCredentials:
            project_name = "testing"
        else:
            project_name = None

        class ExtendedKeysStore(ExtendedKeyspaceMixin, GoogleCloudStore):
            pass

        store = ExtendedKeysStore(
            credentials=gc_credentials, bucket_name=uuid, project=project_name
        )
        yield store
        try_delete_bucket(store._bucket)

    @pytest.fixture(scope="function")
    def store(self, dirty_store):
        for blob in dirty_store._bucket.list_blobs():
            blob.delete()
        if not os.environ.get("STORAGE_EMULATOR_HOST", None):
            time.sleep(0.2)
        return dirty_store


class TestGCExceptions:
    def test_nonexisting_bucket(self, gc_credentials):
        store = GoogleCloudStore(
            credentials=gc_credentials,
            bucket_name="thisbucketdoesntexist123123",
            create_if_missing=False,
        )
        with pytest.raises(google.api_core.exceptions.NotFound):
            store.get("key")
