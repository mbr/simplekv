#!/usr/bin/env python
# coding=utf8

import ConfigParser
import os
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from simplekv.memory.redisstore import RedisStore

from . import testconf_available, testconf_filename, testconf
from . import SimpleKVTest

skip_reason = None if testconf_available else \
            'No redis test configuration supplied. If you wish '\
            'to test the redis-backend, create a file '\
            'called %r with your credentials first. See the '\
            'simplekv.memory.redisstore documentation for details.'\
            % testconf_filename

try:
    import redis
except ImportError:
    skip_reason = 'redis-py required no installed.'


@unittest.skipIf(skip_reason, skip_reason)
class RedisStoreTest(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.redis = redis.StrictRedis(
                host=testconf.get('redis', 'host'),
                port=int(testconf.get('redis', 'port'))
        )
        self.redis.flushdb()

        self.store = RedisStore(self.redis)

    def tearDown(self):
        self.redis.flushdb()
