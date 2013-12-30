#!/usr/bin/env python
# coding=utf8

import os
import shutil
import sys
import stat
import tempfile
from io import BytesIO

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleUrlKVTest
from simplekv._compat import urlparse
from simplekv.fs import FilesystemStore, WebFilesystemStore

from mock import Mock


class TestFileStore(unittest.TestCase, SimpleUrlKVTest):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = FilesystemStore(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    @unittest.skipUnless(os.name == 'posix', 'Not supported outside posix.')
    def test_correct_file_uri(self):
        expected = 'file://' + self.tmpdir + '/somekey'
        self.assertEqual(expected, self.store.url_for('somekey'))

    def test_file_uri(self):
        data = b'Hello, World?!\n'
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.write(data)
            tmpfile.close()

            key = self.store.put_file('testkey', tmpfile.name)
            url = self.store.url_for(key)

            self.assertTrue(url.startswith('file://'))
            parts = urlparse(url)

            with open(parts.path, 'rb') as ndata:
                self.assertEqual(ndata.read(), data)
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)


class TestFileStoreUmask(TestFileStore):
    def setUp(self):
        super(TestFileStoreUmask, self).setUp()

        current_umask = os.umask(0)
        os.umask(current_umask)
        self.perm = 0o666 & (0o777 ^ current_umask)

    def test_file_permission_on_new_file_have_correct_value(self):
        src = BytesIO(b'nonsense')

        key = self.store.put_file('test123', src)

        parts = urlparse(self.store.url_for(key))
        path = parts.path

        mode = os.stat(path).st_mode
        mask = (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        self.assertEqual(mode & mask, self.perm)

    def test_file_permissions_on_moved_in_file_have_correct_value(self):
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        tmpfile.write(b'foo')
        tmpfile.close()
        os.chmod(tmpfile.name, 0o777)
        try:
            key = self.store.put_file('test123', tmpfile.name)

            parts = urlparse(self.store.url_for(key))
            path = parts.path

            mode = os.stat(path).st_mode
            mask = (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

            self.assertEqual(mode & mask, self.perm)
        finally:
            if os.path.exists(tmpfile.name):
                os.path.unlink(tmpfile.name)


class TestFileStorePerm(TestFileStoreUmask):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.perm = 0o612
        self.store = FilesystemStore(self.tmpdir, perm=self.perm)


class TestWebFileStore(unittest.TestCase, SimpleUrlKVTest):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.url_prefix = 'http://some/url/root/'
        self.store = WebFilesystemStore(self.tmpdir, self.url_prefix)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_url(self):
        key = 'some_key'
        expected = self.url_prefix + 'some_key'
        self.assertEqual(self.store.url_for(key), expected)

    def test_url_callable(self):
        prefix = 'http://some.prefix.invalid/'
        mock_callable = Mock(return_value=prefix)

        self.store = WebFilesystemStore(self.tmpdir, mock_callable)

        key = 'mykey'
        expected = prefix + key
        self.assertEqual(self.store.url_for(key), expected)

        mock_callable.assert_called_with(self.store, key)
