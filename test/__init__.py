#!/usr/bin/env python
# coding=utf8

import os
import shutil
import tempfile
from io import BytesIO

from mock import Mock

from simplekv._compat import ConfigParser, xrange


class SimpleKVTest(object):
    def test_store(self):
        self.store.put('key1', b'data1')

    def test_store_and_retrieve(self):
        v = b'data1'
        k = 'key1'
        self.store.put(k, v)
        self.assertEqual(v, self.store.get(k))

    def test_store_and_retrieve_filelike(self):
        v = b'data1'
        k = 'key1'

        self.store.put_file(k, BytesIO(v))
        self.assertEqual(v, self.store.get(k))

    def test_store_and_retrieve_overwrite(self):
        v = b'data1'
        v2 = b'data2'

        k = 'key1'

        self.store.put_file(k, BytesIO(v))
        self.assertEqual(v, self.store.get(k))

        self.store.put(k, v2)
        self.assertEqual(v2, self.store.get(k))

    def test_store_and_open(self):
        v = b'data1'
        k = 'key1'

        self.store.put_file(k, BytesIO(v))
        with self.store.open(k) as blob:
            self.assertEqual(v, blob.read())

    def test_open_incremental_read(self):
        v = b'data_abc'
        k = 'key1'

        self.store.put_file(k, BytesIO(v))
        with self.store.open(k) as ok:
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

    def test_exception_on_invalid_key_get_file(self):
        with self.assertRaises(ValueError):
            self.store.get_file(u'ä', '/dev/null')

        with self.assertRaises(ValueError):
            self.store.get_file('/', '/dev/null')

        with self.assertRaises(ValueError):
            self.store.get_file('\x00', '/dev/null')

        with self.assertRaises(ValueError):
            self.store.get_file('*', '/dev/null')

        with self.assertRaises(ValueError):
            self.store.get_file('', '/dev/null')

    def test_exception_on_invalid_key_delete(self):
        with self.assertRaises(ValueError):
            self.store.delete(u'ä')

        with self.assertRaises(ValueError):
            self.store.delete('/')

        with self.assertRaises(ValueError):
            self.store.delete('\x00')

        with self.assertRaises(ValueError):
            self.store.delete('*')

        with self.assertRaises(ValueError):
            self.store.delete('')

    def test_put_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                k = 'filekey1'
                v = b'somedata'
                tmp.write(v)
                tmp.close()

                self.store.put_file(k, tmp.name)

                self.assertEqual(self.store.get(k), v)
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)

    def test_put_opened_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            k = 'filekey2'
            v = b'somedata2'
            tmp.write(v)
            tmp.flush()

            with open(tmp.name, 'rb') as stream:
                self.store.put_file(k, stream)

            self.assertEqual(self.store.get(k), v)

    def test_get_into_file(self):
        tmpdir = tempfile.mkdtemp()
        try:
            k = 'asdf'
            v = b'123'
            self.store.put(k, v)
            out_filename = os.path.join(tmpdir, 'output')

            self.store.get_file(k, out_filename)

            with open(out_filename, 'rb') as stream:
                self.assertEqual(stream.read(), v)
        finally:
            shutil.rmtree(tmpdir)

    def test_get_into_stream(self):
        k = 'mykey123'
        v = b'another_value'
        self.store.put(k, v)

        output = BytesIO()

        self.store.get_file(k, output)
        self.assertEqual(v, output.getvalue())

    def test_get_nonexistant(self):
        with self.assertRaises(KeyError):
            self.store.get('nonexistantkey')

    def test_get_file_nonexistant(self):
        with self.assertRaises(KeyError):
            self.store.get_file('nonexistantkey', BytesIO())

    def test_get_filename_nonexistant(self):
        with self.assertRaises(KeyError):
            self.store.get_file('nonexistantkey', '/dev/null')

    def test_put_return_value(self):
        k = 'mykey456'
        v = b'some_val'

        rv = self.store.put(k, v)

        self.assertEqual(k, rv)

    def test_put_file_return_value(self):
        k = 'rvkey12'
        v = b'some_val'

        rv = self.store.put_file(k, BytesIO(v))

        self.assertEqual(k, rv)

    def test_put_filename_return_value(self):
        k = 'filenamekey1'
        v = b'some_val'

        tmp = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmp.write(v)
            tmp.close()

            rv = self.store.put_file(k, tmp.name)

            self.assertEqual(rv, k)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_delete(self):
        k = 'key_not_long_this_world'
        v = b'worldy_value'

        self.store.put(k, v)

        self.assertEqual(v, self.store.get(k))

        self.store.delete(k)

        with self.assertRaises(KeyError):
            self.store.get(k)

    def test_multiple_delete_fails_without_error(self):
        k = 'd1'
        v = b'v1'

        self.store.put(k, v)

        self.store.delete(k)
        self.store.delete(k)
        self.store.delete(k)

    def test_can_delete_key_that_never_exists(self):
        self.store.delete('never_ever_existed')

    def test_key_iterator(self):
        self.store.put('key1', b'someval')
        self.store.put('key2', b'someval2')
        self.store.put('key3', b'someval3')

        l = []
        for k in self.store.iter_keys():
            l.append(k)

        l.sort()

        self.assertEqual(l, ['key1', 'key2', 'key3'])

    def test_keys(self):
        self.store.put('key1', b'someval')
        self.store.put('key2', b'someval2')
        self.store.put('key3', b'someval3')

        l = self.store.keys()
        l.sort()

        self.assertEqual(l, ['key1', 'key2', 'key3'])

    def test_has_key(self):
        k = 'keya'
        k2 = 'key2'
        self.store.put(k, b'vala')

        self.assertTrue(k in self.store)
        self.assertFalse(k2 in self.store)

    def test_has_key_with_delete(self):
        k = 'keyb'

        self.assertFalse(k in self.store)

        self.store.put(k, b'valb')
        self.assertTrue(k in self.store)

        self.store.delete(k)
        self.assertFalse(k in self.store)

        self.store.put(k, b'valc')
        self.assertTrue(k in self.store)

    def test_get_with_delete(self):
        k = 'keyb'

        with self.assertRaises(KeyError):
            self.store.get(k)

        self.store.put(k, b'valb')
        self.store.get(k)

        self.store.delete(k)

        with self.assertRaises(KeyError):
            self.store.get(k)

        self.store.put(k, b'valc')
        self.store.get(k)

    def test_max_key_length(self):
        key = 'a' * 250
        val = b'1234'

        new_key = self.store.put(key, val)

        self.assertEqual(new_key, key)
        self.assertEqual(val, self.store.get(key))

    def test_key_special_characters(self):
        key = """'!"`#$%&'()+,-.<=>?@[]^_{}~'"""

        val = b'1234'
        new_key = self.store.put(key, val)

        self.assertEqual(new_key, key)
        self.assertEqual(val, self.store.get(key))

    def test_keys_with_whitespace_rejected(self):
        key = 'an invalid key'

        with self.assertRaises(ValueError):
            new_key = self.store.put(key, b'foo')

    def test_a_lot_of_puts(self):
        a_lot = 20

        for i in xrange(a_lot):
            key = 'this_is_key_%d_of_%d' % (i, a_lot)
            val = os.urandom(512)
            self.store.put(key, val)


class SimpleUrlKVTest(SimpleKVTest):
    def test_url_for_for_generates_url_for(self):
        k = 'uk'
        self.store.put(k, b'v')
        self.assertEqual(type(self.store.url_for(k)), str)

    def test_url_for_generation_does_not_check_exists(self):
        self.store.url_for('does_not_exist_at_all')

    def test_url_for_generation_checks_valid_key(self):
        with self.assertRaises(ValueError):
            self.store.url_for(u'ä')

        with self.assertRaises(ValueError):
            self.store.url_for('/')

        with self.assertRaises(ValueError):
            self.store.url_for('\x00')

        with self.assertRaises(ValueError):
            self.store.url_for('*')

        with self.assertRaises(ValueError):
            self.store.url_for('')


# read test configuration
testconf_filename = os.path.expanduser('~/.simplekv-test')
testconf = ConfigParser.RawConfigParser()
testconf_available = bool(testconf.read(testconf_filename))
