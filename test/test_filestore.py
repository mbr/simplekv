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
from simplekv.fs import FilesystemStore


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
