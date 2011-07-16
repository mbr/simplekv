#!/usr/bin/env python
# coding=utf8

import ConfigParser
import os
import random
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleUrlKVTest

skip_reason = None

# read s3 config
conffile = os.path.expanduser('~/.simplekv-test.boto')
s3conf = ConfigParser.RawConfigParser()
if not s3conf.read(conffile):
    skip_reason = 'No S3 test configuration supplied. If you wish to '\
        'test the S3 backend, create a file called %r with your '\
        'credentials first. See the simplekv.net.s3 documentation '\
        'for details.' % conffile

try:
    from boto.s3.connection import S3Connection
    from boto.exception import S3ResponseError
    import boto
except ImportError:
    skip_reason = 'boto not installed'

if not skip_reason:
    from simplekv.net.botostore import BotoStore


class S3BucketManager(object):
    def create_bucket(self, name=None):
        conn = S3Connection(s3conf.get('s3', 'access_key'),
                            s3conf.get('s3', 'secret_key'))

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


class BucketManagerTest(unittest.TestCase):
    @unittest.skipIf(skip_reason, skip_reason)
    def test_simple(self):
        manager = S3BucketManager()
        bucket = manager.create_bucket()
        manager.drop_bucket(bucket)

    @unittest.skipIf(skip_reason, skip_reason)
    def test_simple_with_contents(self):
        manager = S3BucketManager()
        bucket = manager.create_bucket()
        k = bucket.new_key('i_will_prevent_deletion')
        k.set_contents_from_string('meh')
        manager.drop_bucket(bucket)

    @unittest.skipIf(skip_reason, skip_reason)
    def test_context_manager(self):
        with S3BucketManager() as bucket:
            k = bucket.new_key('test_key')
            k.set_contents_from_string('asdf')

            bucket_name = bucket.name

        conn = S3Connection(s3conf.get('s3', 'access_key'),
                            s3conf.get('s3', 'secret_key'))

        try:
            resp = conn.get_bucket(bucket_name)
        except S3ResponseError, e:
            self.assertEqual(e.code, 'NoSuchBucket')


@unittest.skipIf(skip_reason, skip_reason)
class S3StorageTest(unittest.TestCase, SimpleUrlKVTest):
    def setUp(self):
        self.manager = S3BucketManager()
        self.bucket = self.manager.create_bucket()

        self.store = BotoStore(self.bucket, '/test-prefix')

    def tearDown(self):
        self.manager.drop_bucket(self.bucket)
