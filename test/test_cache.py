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


class TestCacheDecorator(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.backing_store = DictStore()
        self.cache = DictStore()

        self.store = CacheDecorator(self.cache, self.backing_store)

    def test_works_when_cache_loses_key(self):
        self.store.put('keya', 'valuea')
        self.store.put('keyb', 'valueb')

        self.assertEqual('valuea', self.store.get('keya'))
        self.assertEqual('valueb', self.store.get('keyb'))

        del self.store.cache.d['keya']

        self.assertEqual('valuea', self.store.get('keya'))
        self.assertEqual('valueb', self.store.get('keyb'))
