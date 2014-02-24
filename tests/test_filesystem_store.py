# coding: utf8

import os
import stat
from simplekv._compat import BytesIO, url_quote, url_unquote
import tempfile
from simplekv._compat import urlparse

from simplekv.fs import FilesystemStore, WebFilesystemStore
from tempdir import TempDir

from basic_store import BasicStore
from url_store import UrlStore
from idgens import UUIDGen, HashGen

from mock import Mock
import pytest


class TestBaseFilesystemStore(BasicStore, UrlStore, UUIDGen, HashGen):
    @pytest.yield_fixture
    def tmpdir(self):
        with TempDir() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def store(self, tmpdir):
        return FilesystemStore(tmpdir)


class TestFilesystemStoreFileURI(TestBaseFilesystemStore):
    @pytest.mark.skipif(os.name != 'posix',
                        reason='Not supported outside posix.')
    def test_correct_file_uri(self, store, tmpdir, key):
        expected = 'file://' + tmpdir + '/' + url_quote(key)
        assert store.url_for(key) == expected

    def test_file_uri(self, store, value):
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.write(value)
            tmpfile.close()

            key = store.put_file('testkey', tmpfile.name)
            url = store.url_for(key)

            assert url.startswith('file://')
            parts = urlparse(url)

            ndata = open(parts.path, 'rb').read()
            assert value == ndata
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)


# runs each test with a nonstandard umask and checks if it is set correctly
class TestFilesystemStoreUmask(TestBaseFilesystemStore):
    @pytest.fixture(scope='class')
    def current_umask(self):
        mask = os.umask(0)
        # re-set umask
        os.umask(mask)
        return mask

    @pytest.fixture(scope='class')
    def perms(self, current_umask):
        # the permissions we expect on files are inverse to the mask
        return 0o666 & (0o777 ^ current_umask)

    def test_file_permission_on_new_file_have_correct_value(
        self, store, perms, value
    ):
        src = BytesIO(value)

        key = store.put_file('test123', src)

        parts = urlparse(store.url_for(key))
        path = parts.path

        mode = os.stat(path).st_mode
        mask = (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        assert mode & mask == perms

    def test_file_permissions_on_moved_in_file_have_correct_value(
        self, store, perms, key, value
    ):
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        tmpfile.write(value)
        tmpfile.close()
        os.chmod(tmpfile.name, 0o777)
        try:
            key = store.put_file(key, tmpfile.name)

            parts = urlparse(store.url_for(key))
            path = url_unquote(parts.path)

            mode = os.stat(path).st_mode
            mask = (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

            assert mode & mask == perms
        finally:
            if os.path.exists(tmpfile.name):
                os.path.unlink(tmpfile.name)


class TestFileStoreSetPermissions(TestFilesystemStoreUmask):
    @pytest.fixture
    def perms(self):
        return 0o612
        self.tmpdir = tempfile.mkdtemp()

    @pytest.fixture
    def store(self, tmpdir, perms):
        return FilesystemStore(tmpdir, perm=perms)


class TestWebFileStore(TestBaseFilesystemStore):
    @pytest.fixture
    def url_prefix(self):
        return 'http://some/url/root/'

    @pytest.fixture
    def store(self, tmpdir, url_prefix):
        return WebFilesystemStore(tmpdir, url_prefix)

    def test_url(self, store, url_prefix, key):
        expected = url_prefix + url_quote(key)
        assert store.url_for(key) == expected

    def test_url_callable(self, tmpdir, key):
        prefix = 'http://some.prefix.invalid/'
        mock_callable = Mock(return_value=prefix)

        store = WebFilesystemStore(tmpdir, mock_callable)

        expected = prefix + url_quote(key)
        assert store.url_for(key) == expected

        mock_callable.assert_called_with(store, key)
