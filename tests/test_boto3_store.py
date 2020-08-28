#!/usr/bin/env python

import os

import pytest

boto3 = pytest.importorskip('boto3')
from simplekv.net.boto3store import Boto3Store

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
    @pytest.fixture(params=['', '/test-prefix'])
    def prefix(self, request):
        return request.param

    @pytest.fixture
    def store(self, bucket, prefix):
        return Boto3Store(bucket, prefix)

    # Disable max key length test as it leads to problems with minio
    test_max_key_length = None

    def test_get_filename_nonexistant(self, store, key, tmp_path):
        with pytest.raises(KeyError):
            store.get_file(key, os.path.join(str(tmp_path), 'a'))

    def test_key_error_on_nonexistant_get_filename(self, store, key, tmp_path):
        with pytest.raises(KeyError):
            store.get_file(key, os.path.join(str(tmp_path), 'a'))


class TestExtendedKeyspaceBoto3Store(TestBoto3Storage, ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self, bucket, prefix):
        class ExtendedKeyspaceStore(ExtendedKeyspaceMixin, Boto3Store):
            pass
        return ExtendedKeyspaceStore(bucket, prefix)
