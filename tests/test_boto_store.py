#!/usr/bin/env python

import os
from tempdir import TempDir

import pytest

boto = pytest.importorskip('boto')
from simplekv.net.botostore import BotoStore

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
    @pytest.fixture(params=['', '/test-prefix'])
    def prefix(self, request):
        return request.param

    @pytest.fixture
    def store(self, bucket, prefix):
        return BotoStore(bucket, prefix)

    def test_get_filename_nonexistant(self, store):
        # NOTE: boto misbehaves here and tries to erase the target file
        # the parent tests use /dev/null, which you really should not try
        # to os.remove!
        with TempDir() as tmpdir:
            with pytest.raises(KeyError):
                store.get_file('nonexistantkey', os.path.join(tmpdir, 'a'))
