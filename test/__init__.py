#!/usr/bin/env python
# coding=utf8

from StringIO import StringIO
import os
import shutil
import tempfile

from mock import Mock


class SimpleKVTest(object):
    def test_store(self):
        self.store.put('key1', 'data1')

    def test_store_and_retrieve(self):
        v = 'data1'
        k = 'key1'
        self.store.put(k, v)
        self.assertEqual(v, self.store.get(k))

    def test_store_and_retrieve_filelike(self):
        v = 'data1'
        k = 'key1'

        self.store.put_file(k, StringIO(v))
        self.assertEqual(v, self.store.get(k))

    def test_store_and_retrieve_overwrite(self):
        v = 'data1'
        v2 = 'data2'

        k = 'key1'

        self.store.put_file(k, StringIO(v))
        self.assertEqual(v, self.store.get(k))

        self.store.put(k, v2)
        self.assertEqual(v2, self.store.get(k))

    def test_store_and_open(self):
        v = 'data1'
        k = 'key1'

        self.store.put_file(k, StringIO(v))
        self.assertEqual(v, self.store.open(k).read())

    def test_open_incremental_read(self):
        v = 'data_abc'
        k = 'key1'

        self.store.put_file(k, StringIO(v))
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

    def test_put_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            k = 'filekey1'
            v = 'somedata'
            tmp.write(v)
            tmp.flush()

            self.store.put_file(k, tmp.name)

            self.assertEqual(self.store.get(k), v)

    def test_put_opened_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            k = 'filekey2'
            v = 'somedata2'
            tmp.write(v)
            tmp.flush()

            self.store.put_file(k, open(tmp.name, 'rb'))

            self.assertEqual(self.store.get(k), v)

    def test_get_into_file(self):
        tmpdir = tempfile.mkdtemp()
        try:
            k = 'asdf'
            v = '123'
            self.store.put(k, v)
            out_filename = os.path.join(tmpdir, 'output')

            self.store.get_file(k, out_filename)

            self.assertEqual(open(out_filename, 'rb').read(), v)
        finally:
            shutil.rmtree(tmpdir)

    def test_get_into_stream(self):
        k = 'mykey123'
        v = 'another_value'
        self.store.put(k, v)

        output = StringIO()

        self.store.get_file(k, output)
        self.assertEqual(v, output.getvalue())

    def test_put_return_value(self):
        k = 'mykey456'
        v = 'some_val'

        rv = self.store.put(k, v)

        self.assertEqual(k, rv)

    def test_put_file_return_value(self):
        k = 'rvkey12'
        v = 'some_val'

        rv = self.store.put_file(k, StringIO(v))

        self.assertEqual(k, rv)

    def test_put_filename_return_value(self):
        k = 'filenamekey1'
        v = 'some_val'

        (tmpfd, tmpfile) = tempfile.mkstemp()
        try:
            os.write(tmpfd, v)
            os.close(tmpfd)

            rv = self.store.put_file(k, tmpfile)

            self.assertEqual(rv, k)
        finally:
            os.unlink(tmpfile)
