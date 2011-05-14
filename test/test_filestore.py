#!/usr/bin/env python
# coding=utf8

import os
import shutil
import sys
import tempfile

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleUrlKVTest
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
