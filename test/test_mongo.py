#!/usr/bin/env python
# coding=utf8

import sys
import random

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

skip_reason = None
MongoClient = object # To avoid syntax errors
try:
    from pymongo import MongoClient
except ImportError:
    skip_reason = 'MongoDB not installed'

from . import SimpleKVTest
from simplekv.db.mongo import MongoStore


@unittest.skipIf(skip_reason, skip_reason)
class TestMongoDB(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        num_trials = 10
        self.conn = MongoClient()
        for _ in xrange(num_trials):
            rand_num = random.randint(1e7, 1e10)
            self.db_name = "_testing_simplekv_{:x}".format(rand_num)
            if self.db_name not in self.conn.database_names():
                break
        else:
            raise RuntimeError("Can't create a temporary database")
        self.store = MongoStore(self.conn[self.db_name])

    def tearDown(self):
        self.conn.drop_database(self.db_name)
