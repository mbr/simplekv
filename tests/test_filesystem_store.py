# coding: utf8

import os
import stat
from simplekv._compat import BytesIO, url_quote, url_unquote, PY2
import tempfile
from simplekv._compat import urlparse

from simplekv.fs import FilesystemStore, WebFilesystemStore

from basic_store import BasicStore
from url_store import UrlStore
from idgens import UUIDGen, HashGen

from conftest import ExtendedKeyspaceTests
from simplekv.contrib import ExtendedKeyspaceMixin

from mock import Mock
import pytest


class TestBaseFilesystemStore(BasicStore, UrlStore, UUIDGen, HashGen):
    @pytest.yield_fixture
    def tmpdir(self, tmp_path):
        yield str(tmp_path)

    @pytest.fixture
    def store(self, tmpdir):
        return FilesystemStore(tmpdir)


class TestFilesystemStoreMkdir(TestBaseFilesystemStore):

    def test_concurrent_mkdir(self, tmpdir, mocker):
        # Concurrent instantiation of the store in two threads could lead to
        # the situation where both threads see that the directory does not
        # exists. For one, the call to mkdir succeeds, for the other it fails.
        # This is ok for us as long as the directory exists afterwards.
        makedirs = mocker.patch('os.makedirs')
        makedirs.side_effect = OSError("Failure")
        mocker.patch('os.path.isdir')

        store = FilesystemStore(os.path.join(tmpdir, 'test'))
        # We have mocked os.makedirs, so this won't work. But it should
        # pass beyond the OS error and simply fail on writing the file itself.
        if PY2:
            with pytest.raises(IOError):
                store.put('test', b'test')
        else:
            with pytest.raises(FileNotFoundError):
                store.put('test', b'test')


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

            key = store.put_file(u'testkey', tmpfile.name)
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

        key = store.put_file(u'test123', src)

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


class TestExtendedKeyspaceFilesystemStore(TestBaseFilesystemStore,
                                          ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self, tmpdir):
        class ExtendedKeyspaceStore(ExtendedKeyspaceMixin, FilesystemStore):
            pass
        return ExtendedKeyspaceStore(tmpdir)

    def test_prefix_iterator_ossep(self, store, value):
        delimiter = u"X"
        for k in [
            u"a1" + os.sep + u"b1",
            u"a1" + os.sep + u"b1",
            u"a2" + os.sep + u"b1",
            u"a3",
            u"a4" + os.sep + u"b1" + os.sep + u"c1",
            u"a4" + os.sep + u"b1" + os.sep + u"c2",
            u"a4" + os.sep + u"b2" + os.sep + u"c1",
            u"a4" + os.sep + u"b3",
        ]:
            store.put(k, value)

        l = sorted(store.iter_prefixes(os.sep))
        assert l == [
            u"a1" + os.sep,
            u"a2" + os.sep,
            u"a3",
            u"a4" + os.sep,
        ]

        l = sorted(store.iter_prefixes(
            os.sep,
            prefix=u"a4" + os.sep,
        ))
        assert l == [
            u"a4" + os.sep + "b1" + os.sep,
            u"a4" + os.sep + "b2" + os.sep,
            u"a4" + os.sep + "b3",
        ]

        l = sorted(store.iter_prefixes(
            os.sep,
            prefix=u"foo" + os.sep,
        ))
        assert l == []
