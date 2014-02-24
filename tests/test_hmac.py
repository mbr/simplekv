import hmac
import os
from simplekv._compat import BytesIO, xrange
import tempfile

from simplekv.crypt import _HMACFileReader, VerificationException,\
    HMACDecorator

from six import b, indexbytes, int2byte
import pytest


class TestHMACFileReader(object):
    @pytest.fixture
    def bad_datas(self, value):
        val = value * 3

        def _alter_byte(byte_string, pos):
            old_val = indexbytes(byte_string, pos)
            new_byte = int2byte((old_val + 1 % 255))
            return byte_string[:pos] + new_byte + byte_string[pos + 1:]

        return (_alter_byte(val, i) for i in xrange(len(val)))

    @pytest.fixture
    def expected_digest(self, secret_key, value, hashfunc):
        return hmac.HMAC(secret_key, value, hashfunc).digest()

    @pytest.fixture
    def stored_blob(self, value, expected_digest):
        return value + expected_digest

    @pytest.fixture
    def create_reader(self, stored_blob, secret_key, hashfunc):
        return lambda: _HMACFileReader(hmac.HMAC(secret_key, None, hashfunc),
                                       BytesIO(stored_blob))

    @pytest.fixture
    def chunk_sizes(self, value):
        return [10 ** n for n in xrange(2, 8)]

    def test_reading_limit_0(self, create_reader):
        reader = create_reader()
        assert reader.read(0) == ''
        assert reader.read(0) == ''

    def test_reading_with_limit(self, secret_key, hashfunc, value,
                                create_reader, chunk_sizes):
        # try for different read lengths
        for n in chunk_sizes:
            chunks = []
            reader = create_reader()
            while True:
                r = reader.read(n)
                if not r:
                    break
                chunks.append(r)

            assert b('').join(chunks) == value

    def test_manipulated_input_full_read(
        self, secret_key, value, bad_datas, hashfunc
    ):
        for bad_data in bad_datas:
            reader = _HMACFileReader(
                hmac.HMAC(secret_key, None, hashfunc),
                BytesIO(bad_data)
            )

            with pytest.raises(VerificationException):
                reader.read()

    def test_manipulated_input_incremental_read(
        self, secret_key, bad_datas, hashfunc
    ):
        for bad_data in bad_datas:
            reader = _HMACFileReader(
                hmac.HMAC(secret_key, None, hashfunc),
                BytesIO(bad_data)
            )

            with pytest.raises(VerificationException):
                bitesize = 100
                while True:
                    if len(reader.read(bitesize)) != bitesize:
                        break

    def test_input_too_short(self, secret_key, hashfunc):
        with pytest.raises(VerificationException):
            _HMACFileReader(
                hmac.HMAC(secret_key, None, hashfunc),
                BytesIO(b('a'))
            )

    def test_unbounded_read(self, value, create_reader):
        assert create_reader().read() == value


# test the "real" HMACMixin: core functionality and checks
# this only works with dicts, as we access the internal structures to
# manipulate values
class HMACDec(object):
    @pytest.fixture
    def hmacstore(self, secret_key, store):
        return HMACDecorator(secret_key, store)

    def test_get_fails_on_manipulation(self, hmacstore, key, value):
        hmacstore.put(key, value)
        hmacstore.d[key] += b('a')

        with pytest.raises(VerificationException):
            hmacstore.get(key)

    def test_get_file_fails_on_manipulation(self, hmacstore, key, value):
        hmacstore.put(key, value)
        hmacstore.d[key] += b('a')

        with tempfile.TemporaryFile() as tmp:
            with pytest.raises(VerificationException):
                hmacstore.get_file(key, tmp)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                with pytest.raises(VerificationException):
                    hmacstore.get_file(key, tmp.name)
            finally:
                os.unlink(tmp.name)

    def test_open_fails_on_manipulation(self, hmacstore, key, value):
        hmacstore.put(key, value)
        hmacstore.d[key] += b('a')

        with pytest.raises(VerificationException):
            hmacstore.open(key).read()

        handle = hmacstore.open(key)

        # we read 1 extra byte now, because the value is actually longer
        handle.read(len(value) + 1)

        with pytest.raises(VerificationException):
            handle.read(1)

    def test_get_fails_on_replay_manipulation(
        self, hmacstore, key, key2, value
    ):
        hmacstore.put(key, value)
        hmacstore.d[key2] = hmacstore.d[key]
        hmacstore.get(key)

        with pytest.raises(VerificationException):
            hmacstore.get(key2)
