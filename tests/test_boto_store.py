#!/usr/bin/env python

import os
from tempdir import TempDir

import pytest

boto = pytest.importorskip('boto')
from simplekv.net.botostore import BotoStore
from simplekv._compat import BytesIO

from basic_store import BasicStore
from url_store import UrlStore
from bucket_manager import boto_credentials, boto_bucket


@pytest.fixture(params=boto_credentials,
                ids=[c['access_key'] for c in boto_credentials])
def credentials(request):
    return request.param


@pytest.yield_fixture()
def bucket(credentials):
    with boto_bucket(**credentials) as bucket:
        yield bucket


class TestBotoStorage(BasicStore, UrlStore):
    @pytest.fixture(params=[True, False])
    def reduced_redundancy(self, request):
        return request.param

    @pytest.fixture
    def storage_class(self, reduced_redundancy):
        return 'REDUCED_REDUNDANCY' if reduced_redundancy else 'STANDARD'

    @pytest.fixture(params=['', '/test-prefix'])
    def prefix(self, request):
        return request.param

    @pytest.fixture
    def store(self, bucket, prefix, reduced_redundancy):
        return BotoStore(bucket, prefix, reduced_redundancy=reduced_redundancy)

    def test_get_filename_nonexistant(self, store, key):
        # NOTE: boto misbehaves here and tries to erase the target file
        # the parent tests use /dev/null, which you really should not try
        # to os.remove!
        with TempDir() as tmpdir:
            with pytest.raises(KeyError):
                store.get_file(key, os.path.join(tmpdir, 'a'))

    def test_key_error_on_nonexistant_get_filename(self, store, key):
        with TempDir() as tmpdir:
            with pytest.raises(KeyError):
                store.get_file(key, os.path.join(tmpdir, 'a'))

    def test_storage_class_put(
        self, store, prefix, key, value, storage_class, bucket
    ):
        store.put(key, value)

        keyname = prefix + key

        if storage_class != 'STANDARD':
            pytest.xfail('boto does not support checking the storage class?')

        assert bucket.lookup(keyname).storage_class == storage_class

    def test_storage_class_putfile(
        self, store, prefix, key, value, storage_class, bucket
    ):
        store.put_file(key, BytesIO(value))

        keyname = prefix + key

        if storage_class != 'STANDARD':
            pytest.xfail('boto does not support checking the storage class?')
        assert bucket.lookup(keyname).storage_class == storage_class
