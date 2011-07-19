#!/usr/bin/env python
# coding=utf8

import ConfigParser
import os
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from simplekv.memory.memcachestore import MemcacheStore

from . import testconf_available, testconf_filename, testconf
from . import SimpleKVTest

skip_reason = None if testconf_available else \
            'No memcache test configuration supplied. If you wish '\
            'to test the memcached-backend, create a file '\
            'called %r with your credentials first. See the '\
            'simplekv.memory.memcachestore documentation for details.'\
            % testconf_filename

try:
    from memcache import Client
except ImportError:
    try:
        from pylibmc import Client
    except ImportError:
        skip_reason = 'Neither python-memcache nor pylibmc installed.'


@unittest.skipIf(skip_reason, skip_reason)
class MemcacheStoreTest(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.mc = Client([testconf.get('memcache', 'server')])
        self.mc.flush_all()

        self.store = MemcacheStore(self.mc)

    def tearDown(self):
        self.mc.flush_all()

    def test_memcache_connection(self):
        pass

    # disabled tests (not fully API support for memcache)
    test_has_key = None
    test_has_key_with_delete = None
    test_key_iterator = None
    test_keys = None

    def test_keys_throws_io_error(self):
        with self.assertRaises(IOError):
            self.store.keys()

        with self.assertRaises(IOError):
            self.store.iter_keys()

        with self.assertRaises(IOError):
            iter(self.store)

    def test_contains_throws_io_error_or_succeeds(self):
        try:
            'a' in self.store
        except IOError:
            pass
