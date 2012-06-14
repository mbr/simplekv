#!/usr/bin/env python
# coding=utf8

import sys
import unittest

from test import SimpleKVTest


class GaeBackendTest(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        if not 'dev_appserver' in sys.modules:
            self.skipTest('Need to run this with app engine SDK installed.')

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.store = NdbStore(TestStoreModel)

    def tearDown(self):
        self.testbed.deactivate()

    def test_app_engine_tests_work(self):
        item = TestStoreModel(v='foo')
        item.put()


if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('google_app_engine_path')
    args = parser.parse_args()
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, args.google_app_engine_path)

    import dev_appserver
    dev_appserver.fix_sys_path()

    # import stuff
    from google.appengine.ext import ndb, testbed
    from simplekv.gae import NdbStore

    class TestStoreModel(ndb.Model):
        v = ndb.BlobProperty(indexed=False)

    # run suite
    suite = unittest.TestLoader().loadTestsFromTestCase(GaeBackendTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
