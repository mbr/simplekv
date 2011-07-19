#!/usr/bin/env python
# coding=utf8

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import testconf_available, testconf, testconf_filename

s3_available = False
gs_available = False
try:
    import boto
    from boto.exception import StorageResponseError
except ImportError:
    skip_reason = 'Boto library not installed.'
else:
    # read config file when module is loaded
    skip_reason = None
    if not testconf_available:
        skip_reason = 'No boto test configuration supplied. If you wish '\
            'to test the S3 or Google Storage backend, create a file '\
            'called %r with your credentials first. See the '\
            'simplekv.net.botostore documentation for details.'\
            % testconf_filename
    else:
        s3_available = testconf.has_section('s3')
        gs_available = testconf.has_section('gs')
        import random

        class BucketManager(object):
            def create_bucket(self, name=None):
                conn = self.connection_func(
                    testconf.get(self.config_section, 'access_key'),
                    testconf.get(self.config_section, 'secret_key'))

                name = name or 'simplekv-unittest-%x' %\
                    random.SystemRandom().getrandbits(64)

                bucket = conn.create_bucket(name)

                return bucket

            def drop_bucket(self, bucket):
                for key in bucket.list():
                    key.delete()
                bucket.delete()

            # context manager for an s3 bucket
            def __enter__(self):
                self.bucket = self.create_bucket()
                return self.bucket

            def __exit__(self, *args):
                if getattr(self, 'bucket', None):
                    self.drop_bucket(self.bucket)

        class S3BucketManager(BucketManager):
            config_section = 's3'
            connection_func = staticmethod(boto.connect_s3)

        class GSBucketManager(BucketManager):
            config_section = 'gs'
            connection_func = staticmethod(boto.connect_gs)


class BucketManagerTest():
    @unittest.skipIf(skip_reason, skip_reason)
    def test_simple(self):
        manager = self.manager_class()
        bucket = manager.create_bucket()
        manager.drop_bucket(bucket)

    @unittest.skipIf(skip_reason, skip_reason)
    def test_simple_with_contents(self):
        manager = self.manager_class()
        bucket = manager.create_bucket()
        k = bucket.new_key('i_will_prevent_deletion')
        k.set_contents_from_string('meh')
        manager.drop_bucket(bucket)

    @unittest.skipIf(skip_reason, skip_reason)
    def test_context_manager(self):
        with self.manager_class() as bucket:
            k = bucket.new_key('test_key')
            k.set_contents_from_string('asdf')

            bucket_name = bucket.name

        conn = self.manager_class.connection_func(
                 testconf.get(self.manager_class.config_section, 'access_key'),
                 testconf.get(self.manager_class.config_section, 'secret_key'))
        try:
            resp = conn.get_bucket(bucket_name)
        except StorageResponseError, e:
            self.assertEqual(e.code, 'NoSuchBucket')


@unittest.skipUnless(s3_available, 'No S3 credentials available.')
class S3BucketManagerTest(unittest.TestCase, BucketManagerTest):
    manager_class = S3BucketManager


@unittest.skipUnless(gs_available, 'No Google Storage credentials available.')
class GSBucketManagerTest(unittest.TestCase, BucketManagerTest):
    manager_class = GSBucketManager
