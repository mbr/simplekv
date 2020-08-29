#!/usr/bin/env python

import os

import pytest

boto3 = pytest.importorskip('boto3')
from simplekv.net.boto3store import Boto3Store
from simplekv._compat import BytesIO

from basic_store import BasicStore
from url_store import UrlStore
from bucket_manager import boto_credentials, boto3_bucket
from conftest import ExtendedKeyspaceTests
from simplekv.contrib import ExtendedKeyspaceMixin


@pytest.fixture(params=boto_credentials,
                ids=[c['access_key'] for c in boto_credentials])
def credentials(request):
    return request.param


@pytest.yield_fixture()
def bucket(credentials):
    with boto3_bucket(**credentials) as bucket:
        yield bucket


class TestBoto3Storage(BasicStore, UrlStore):
    @pytest.fixture(params=[True, False])
    def reduced_redundancy(self, request):
        return request.param

    @pytest.fixture
    def storage_class(self, reduced_redundancy):
        return 'REDUCED_REDUNDANCY' if reduced_redundancy else None

    @pytest.fixture(params=['', '/test-prefix'])
    def prefix(self, request):
        return request.param

    @pytest.fixture
    def store(self, bucket, prefix, reduced_redundancy):
        return Boto3Store(bucket, prefix, reduced_redundancy=reduced_redundancy)

    # Disable max key length test as it leads to problems with minio
    test_max_key_length = None

    def test_get_filename_nonexistant(self, store, key, tmp_path):
        with pytest.raises(KeyError):
            store.get_file(key, os.path.join(str(tmp_path), 'a'))

    def test_key_error_on_nonexistant_get_filename(self, store, key, tmp_path):
        with pytest.raises(KeyError):
            store.get_file(key, os.path.join(str(tmp_path), 'a'))

    def test_storage_class_put(
        self, store, prefix, key, value, storage_class, bucket
    ):
        store.put(key, value)
        obj = bucket.Object(prefix.lstrip('/') + key)
        assert obj.storage_class == storage_class

    def test_storage_class_putfile(
        self, store, prefix, key, value, storage_class, bucket
    ):
        store.put_file(key, BytesIO(value))
        obj = bucket.Object(prefix.lstrip('/') + key)
        assert obj.storage_class == storage_class


class TestExtendedKeyspaceBoto3Store(TestBoto3Storage, ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self, bucket, prefix, reduced_redundancy):
        class ExtendedKeyspaceStore(ExtendedKeyspaceMixin, Boto3Store):
            pass
        return ExtendedKeyspaceStore(bucket, prefix,
                                     reduced_redundancy=reduced_redundancy)
