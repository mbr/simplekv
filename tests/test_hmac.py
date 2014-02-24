import hmac
import os
from simplekv._compat import BytesIO
import tempfile

from simplekv.crypt import _HMACFileReader, VerificationException,\
    HMACDecorator

import pytest


class TestHMACFileReader(object):
    # setup for correct data
    @pytest.fixture(params=[
        ('helloworld!@\xa9;\x99\xfai0\xb9!2\xd7\x82\xf4\xf3g\xf8\xa9'
         'xcd\xcf\xff'),
        '\x99\xfai0\xb9!2\xd7\x82\xf4\xf3' * 1024 * 4,
        'vryshrt',
        '\x00\x00',
        '8b97bca79750847558d488e2ea4de79903c9c71c9af27ecf1b3dff5dba2abdd9',
    ])
    def sample_data(self, request):
        return request.param

    @pytest.fixture
    def bad_datas(self, sample_data):
        def _alter_byte(s, n):
            return s[:n] + chr((ord(s[n]) + 1) % 255) + s[n + 1:]

        return (_alter_byte(sample_data, i) for i in range(len(sample_data)))

    @pytest.fixture
    def expected_digest(self, secret_key, sample_data, hashfunc):
        return hmac.HMAC(secret_key, sample_data, hashfunc).digest()

    @pytest.fixture
    def stored_blob(self, sample_data, expected_digest):
        return sample_data + expected_digest

    @pytest.fixture
    def create_reader(self, stored_blob, secret_key, hashfunc):
        return lambda: _HMACFileReader(hmac.HMAC(secret_key, None, hashfunc),
                                       BytesIO(stored_blob))

    @pytest.fixture
    def chunk_sizes(self, sample_data):
        return [10 ** n for n in xrange(2, 8)]

    def test_reading_limit_0(self, create_reader):
        reader = create_reader()
        assert reader.read(0) == ''
        assert reader.read(0) == ''

    def test_reading_with_limit(self, secret_key, hashfunc, sample_data,
                                create_reader, chunk_sizes):
        # try for different read lengths
        for n in chunk_sizes:
            data = ''
            reader = create_reader()
            while True:
                r = reader.read(n)
                if '' == r:
                    break
                data += r

            assert data == sample_data

    def test_manipulated_input_full_read(
        self, secret_key, sample_data, bad_datas, hashfunc
    ):
        for bad_data in bad_datas:
            reader = _HMACFileReader(
                hmac.HMAC(secret_key, None, hashfunc),
                BytesIO(bad_datas)
            )

            with pytest.raises(VerificationException):
                reader.read()

    def test_manipulated_input_incremental_read(
        self, secret_key, bad_datas, hashfunc
    ):
        for bad_data in bad_datas:
            reader = _HMACFileReader(
                hmac.HMAC(secret_key, None, hashfunc),
                BytesIO(bad_datas)
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
                BytesIO('a')
            )

    def test_unbounded_read(self, sample_data, create_reader):
        assert create_reader().read() == sample_data


# test the "real" HMACMixin: core functionality and checks
# this only works with dicts, as we access the internal structures to
# manipulate values
class HMACDec(object):
    @pytest.fixture
    def hmacstore(self, secret_key, store):
        return HMACDecorator(secret_key, store)

    def test_get_fails_on_manipulation(self, hmacstore):
        hmacstore.put('the_key', 'somevalue')
        hmacstore.d['the_key'] += 'a'

        with pytest.raises(VerificationException):
            hmacstore.get('the_key')

    def test_get_file_fails_on_manipulation(self, hmacstore):
        k = 'the_key!'
        hmacstore.put(k, 'somevalue')
        hmacstore.d[k] += 'a'

        with tempfile.TemporaryFile() as tmp:
            with pytest.raises(VerificationException):
                hmacstore.get_file(k, tmp)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            try:
                with pytest.raises(VerificationException):
                    hmacstore.get_file(k, tmp.name)
            finally:
                os.unlink(tmp.name)

    def test_open_fails_on_manipulation(self, hmacstore):
        k = 'the_key!'
        v = 'somevalue'

        hmacstore.put(k, v)
        hmacstore.d[k] += 'a'

        with pytest.raises(VerificationException):
            hmacstore.open(k).read()

        handle = hmacstore.open(k)

        # we read 1 extra byte now, because the value is actually longer
        handle.read(len(v) + 1)

        with pytest.raises(VerificationException):
            handle.read(1)

    def test_get_fails_on_replay_manipulation(self, hmacstore):
        k = 'somekey'
        evil = 'evilkey'

        hmacstore.put(k, 'myvalue')
        hmacstore.d[evil] = hmacstore.d[k]
        hmacstore.get(k)

        with pytest.raises(VerificationException):
            hmacstore.get(evil)
