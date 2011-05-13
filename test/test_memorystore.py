#!/usr/bin/env python
# coding=utf8

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleKVTest
from simplekv.memory import DictStore


class TestDictStore(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.store = DictStore()
