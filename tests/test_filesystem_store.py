# coding: utf8

from simplekv.fs import FilesystemStore
from tempdir import TempDir

from basic_store import BasicStore
from url_store import UrlStore
from idgens import UUIDGen, HashGen

import pytest


class TestFilesystemStore(BasicStore, UrlStore, UUIDGen, HashGen):
    @pytest.yield_fixture
    def store(self):
        with TempDir() as tmpdir:
            yield FilesystemStore(tmpdir)
