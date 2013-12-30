#!/usr/bin/env python
# coding=utf8

import hashlib
import hmac
import os
import sys
import tempfile
import itertools
from io import BytesIO
from functools import partial

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from simplekv.crypt import _HMACFileReader, VerificationException,\
                           HMACDecorator
from simplekv.memory import DictStore
from simplekv._compat import xrange
from . import SimpleKVTest


def _alter_byte(s, n):
    try:
        return s[:n] + bytes((s[n] + 1) % 255) + s[n + 1:]  # python3
    except TypeError:
        return s[:n] + chr((ord(s[n]) + 1) % 255) + s[n + 1:]  # python2


class TestHMACFileReader(unittest.TestCase):
    secret_key = b'devkey##123'
    data = b'helloworld!'\
           b'@\xa9;\x99\xfai0\xb9!2\xd7\x82\xf4\xf3g\xf8\xa9\xcd\xcf\xff'
    hashfunc = hashlib.sha256
    expected_digest = b'\x05n\xbc\x91\x02\x171\xe1G\xcc\xd6\xc6\x01'\
                      b'\xc4\x0b+W\xb8W\xb1\x027\x03\xf2B\x98\xf7'\
                      b'\xb4\xf7\x91KD'
    stored_data_and_hash = data + expected_digest
    reading_lengths = range(1, len(data) * 3)

    def setUp(self):
        self.buf = BytesIO(self.stored_data_and_hash)
        self.hm = hmac.HMAC(self.secret_key, None, self.hashfunc)
        self.reader = _HMACFileReader(self.hm, self.buf)

    def test_setUp_is_correct(self):
        hm = hmac.HMAC(self.secret_key, self.data, self.hashfunc)

        self.assertEqual(hm.digest(), self.expected_digest)

    def test_reading_limit_0(self):
        self.assertEqual('', self.reader.read(0))
        self.assertEqual('', self.reader.read(0))

    def test_reading_with_limit(self):
        # try for different read lengths
        for n in self.reading_lengths:
            buf = BytesIO(self.stored_data_and_hash)
            hm = hmac.HMAC(self.secret_key, None, self.hashfunc)

            reader = _HMACFileReader(hm, buf)

            data = b''.join(iter(partial(reader.read, n), b''))

            self.assertEqual(data, self.data)

    def test_manipulated_input_full_read(self):
        sizes = itertools.chain(range(0, 20), range(-1, -20, -1))
        for n in sizes:
            broken_stored_data_and_hash = _alter_byte(
                self.stored_data_and_hash,
                n
            )

            reader = _HMACFileReader(
                hmac.HMAC(self.secret_key, None, self.hashfunc),
                BytesIO(broken_stored_data_and_hash)
            )

            with self.assertRaises(VerificationException):
                reader.read()

    def test_manipulated_input_incremental_read(self):
        sizes = itertools.chain(range(0, 20), range(-1, -20, -1))
        for n in sizes:
            broken_stored_data_and_hash = _alter_byte(
                self.stored_data_and_hash,
                n
            )

            reader = _HMACFileReader(
                hmac.HMAC(self.secret_key, None, self.hashfunc),
                BytesIO(broken_stored_data_and_hash)
            )

            with self.assertRaises(VerificationException):
                bitesize = 100
                while True:
                    if len(reader.read(bitesize)) != bitesize:
                        break

    def test_input_too_short(self):
        with self.assertRaises(VerificationException):
            reader = _HMACFileReader(
                hmac.HMAC(self.secret_key, None, self.hashfunc),
                BytesIO(b'a')
            )

    def test_unbounded_read(self):
        self.assertEqual(self.data, self.reader.read())


# run all tests on input that is shorter/longer/equal than the hash
class TestHMACFileReaderLongInput(TestHMACFileReader):
    data = b'\x99\xfai0\xb9!2\xd7\x82\xf4\xf3' * 1024 * 1024
    expected_digest = hmac.HMAC(
        TestHMACFileReader.secret_key, data, TestHMACFileReader.hashfunc
    ).digest()
    stored_data_and_hash = data + expected_digest

    reading_lengths = [10 ** n for n in xrange(2, 8)]


class TestHMACFileReaderShortInput(TestHMACFileReader):
    data = b'aca4'
    expected_digest = hmac.HMAC(
        TestHMACFileReader.secret_key, data, TestHMACFileReader.hashfunc
    ).digest()
    stored_data_and_hash = data + expected_digest

    reading_lengths = range(1, 100)


class TestHMACFileReaderEqualInput(TestHMACFileReader):
    # this string is as long as a sha256 sum
    data = b'8b97bca79750847558d488e2ea4de79903c9c71c9af27ecf1b3dff5dba2abdd9'
    expected_digest = hmac.HMAC(
        TestHMACFileReader.secret_key, data, TestHMACFileReader.hashfunc
    ).digest()
    stored_data_and_hash = data + expected_digest

    reading_lengths = range(1, 100)


# different digest algorithm and key
class TestHMACFileReaderDifferentHashfuncAndKey(TestHMACFileReader):
    # this string is as long as a sha256 sum
    hashfunc = hashlib.sha1
    secret_key = b'secret_key_b'
    expected_digest = hmac.HMAC(
        secret_key, TestHMACFileReader.data, hashfunc
    ).digest()
    stored_data_and_hash = TestHMACFileReader.data + expected_digest

    reading_lengths = range(1, 100)


# test the "real" now HMACMixin: core functionality and checks
class TestHMACDictBackend(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        self.store = HMACDecorator(b'my_secret_key', DictStore())

    def test_get_fails_on_manipulation(self):
        self.store.put('the_key', b'somevalue')

        self.store.d['the_key'] += b'a'
        with self.assertRaises(VerificationException):
            val = self.store.get('the_key')

    def test_get_file_fails_on_manipulation(self):
        k = 'the_key!'
        self.store.put(k, b'somevalue')

        self.store.d[k] += b'a'

        with tempfile.TemporaryFile() as tmp:
            with self.assertRaises(VerificationException):
                val = self.store.get_file(k, tmp)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                with self.assertRaises(VerificationException):
                    val = self.store.get_file(k, tmp.name)
            finally:
                os.unlink(tmp.name)

    def test_open_fails_on_manipulation(self):
        k = 'the_key!'
        v = b'somevalue'
        self.store.put(k, v)

        self.store.d[k] += b'a'
        with self.assertRaises(VerificationException):
            val = self.store.open(k).read()

        handle = self.store.open(k)

        # we read 1 extra byte now, because the value is actually l onger
        handle.read(len(v) + 1)
        with self.assertRaises(VerificationException):
            handle.read(1)

    def test_get_fails_on_replay_manipulation(self):
        k = 'somekey'
        evil = 'evilkey'
        self.store.put(k, b'myvalue')

        self.store.d[evil] = self.store.d[k]

        self.store.get(k)

        with self.assertRaises(VerificationException):
            self.store.get(evil)
