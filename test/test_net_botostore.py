#!/usr/bin/env python
# coding=utf8

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleUrlKVTest
import test_bucket_manager

if test_bucket_manager.s3_available or test_bucket_manager.gs_available:
    from simplekv.net.botostore import BotoStore


@unittest.skipUnless(test_bucket_manager.s3_available, 'S3 not available')
class S3StorageTest(unittest.TestCase, SimpleUrlKVTest):
    def setUp(self):
        self.manager = test_bucket_manager.S3BucketManager()
        self.bucket = self.manager.create_bucket()
        self.store = BotoStore(self.bucket, '/test-prefix')

    def tearDown(self):
        self.manager.drop_bucket(self.bucket)


@unittest.skipUnless(test_bucket_manager.gs_available,
                     'Google Storage not available')
class GSStorageTest(unittest.TestCase, SimpleUrlKVTest):
    def setUp(self):
        self.manager = test_bucket_manager.GSBucketManager()
        self.bucket = self.manager.create_bucket()
        self.store = BotoStore(self.bucket, '/test-prefix')

    def tearDown(self):
        self.manager.drop_bucket(self.bucket)
