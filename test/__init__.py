#!/usr/bin/env python
# coding=utf8

from mock import Mock

from StringIO import StringIO

class SimpleKVTest(object):
    def test_store(self):
        self.store.put('key1', 'data1')

    def test_store_and_retrieve(self):
        v = 'data1'
        k = 'key1'
        self.store.put(k,v)
        self.assertEqual(v, self.store.get(k))

    def test_store_and_retrieve_filelike(self):
        v = 'data1'
        k = 'key1'

        self.store.put(k, StringIO(v))
        self.assertEqual(v, self.store.get(k))

    def test_store_and_retrieve_overwrite(self):
        v = 'data1'
        v2 = 'data2'

        k = 'key1'

        self.store.put(k, StringIO(v))
        self.assertEqual(v, self.store.get(k))

        self.store.put(k, v2)
        self.assertEqual(v2, self.store.get(k))

    def test_store_and_open(self):
        v = 'data1'
        k = 'key1'

        self.store.put(k, StringIO(v))
        self.assertEqual(v, self.store.open(k).read())

    def test_open_incremental_read(self):
        v = 'data_abc'
        k = 'key1'

        self.store.put(k, StringIO(v))
        ok = self.store.open(k)
        self.assertEqual(v[:3], ok.read(3))
        self.assertEqual(v[3:5], ok.read(2))
        self.assertEqual(v[5:8], ok.read(3))

    def test_key_error_on_nonexistant_get(self):
        with self.assertRaises(KeyError):
            self.store.get('doesnotexist')

    def test_key_error_on_nonexistant_open(self):
        with self.assertRaises(KeyError):
            self.store.open('doesnotexist')

    def test_exception_on_invalid_key_get(self):
        with self.assertRaises(ValueError):
            self.store.get(u'ä')

        with self.assertRaises(ValueError):
            self.store.get('/')

        with self.assertRaises(ValueError):
            self.store.get('\x00')

        with self.assertRaises(ValueError):
            self.store.get('*')

        with self.assertRaises(ValueError):
            self.store.get('')
