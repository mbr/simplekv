#!/usr/bin/env python
# coding=utf8

import os
import shutil
import sys
import tempfile
import uuid

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from . import SimpleKVTest, SimpleUrlKVTest
from simplekv.memory import DictStore
from simplekv.idgen import UUIDDecorator, HashDecorator
from simplekv.fs import FilesystemStore


UUID_REGEXP = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'


class TestUUIDGen(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.store = UUIDDecorator(DictStore())

    def test_put_generates_uuid_form(self):
        key = self.store.put(None, 'some_data')
        self.assertRegexpMatches(key, UUID_REGEXP)

    def test_put_file_generates_uuid_form(self):
        key = self.store.put_file(None, open('/dev/null', 'rb'))
        self.assertRegexpMatches(key, UUID_REGEXP)

        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.close()
            key2 = self.store.put_file(None, tmpfile.name)
            self.assertRegexpMatches(key2, UUID_REGEXP)
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)

    def test_put_generates_valid_uuid(self):
        key = self.store.put(None, 'some_data')
        uuid.UUID(hex=key)

    def test_put_file_generates_valid_uuid(self):
        key = self.store.put_file(None, open('/dev/null', 'rb'))
        uuid.UUID(hex=key)

        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.close()
            key2 = self.store.put_file(None, tmpfile.name)
            uuid.UUID(hex=key2)
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)


class TestUUIDGenFilesystem(TestUUIDGen, SimpleUrlKVTest):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = UUIDDecorator(FilesystemStore(self.tmpdir))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestHashGen(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.store = HashDecorator(DictStore())
        self.hash_regexp = r'^[0-9a-f]{%d}$' % (
            self.store.hashfunc().digest_size * 2,
        )

    def test_put_generates_valid_form(self):
        key = self.store.put(None, 'some_data')
        self.assertRegexpMatches(key, self.hash_regexp)

    def test_put_file_generates_valid_form(self):
        key = self.store.put_file(None, open('/dev/null', 'rb'))
        self.assertRegexpMatches(key, self.hash_regexp)

        # this is not correct according to our interface
        # /dev/null cannot be claimed by the store
        # key2 = self.store.put_file(None, '/dev/null')
        # self.assertRegexpMatches(key2, self.hash_regexp)

    def test_put_generates_correct_hash(self):
        data = 'abcdXefg'
        key = self.store.put(None, data)

        hash = self.store.hashfunc(data).hexdigest()

        self.assertEqual(hash, key)

    def test_put_file_generates_correct_hash(self):
        data = '!bcdXefQ'
        hash = self.store.hashfunc(data).hexdigest()
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.write(data)
            tmpfile.close()
            with open(tmpfile.name, 'rb') as f:
                key = self.store.put_file(None, f)
            self.assertEqual(key, hash)

            key2 = self.store.put_file(None, tmpfile.name)
            self.assertEqual(key2, hash)
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)

    def test_put_hashfunc_is_sha1(self):
        data = 'some_test_string'
        hash = '7a3ae7e083965679a6965e4a4d89c5f0d6a1f7e4'

        self.assertEqual(self.store.put(None, data), hash)


class TestHashGenFilesystem(TestHashGen, SimpleUrlKVTest):
    def setUp(self):
        TestHashGen.setUp(self)
        self.tmpdir = tempfile.mkdtemp()
        self.store = HashDecorator(FilesystemStore(self.tmpdir))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
