#!/usr/bin/env python
# coding=utf8

import shutil
import sys
import tempfile

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleKVTest
from simplekv.fs import FilesystemStore


class TestFileStorage(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = FilesystemStore(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
