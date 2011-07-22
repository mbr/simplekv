#!/usr/bin/env python
# coding=utf8

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleKVTest
from simplekv.memory import DictStore
from simplekv.cache import CacheDecorator


class TestCachingDecorator(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.backing_store = DictStore()
        self.cache = DictStore()

        self.store = CacheDecorator(self.cache, self.backing_store)
