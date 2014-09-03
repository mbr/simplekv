# coding: utf8

import os
import time
import tempfile
from tempdir import TempDir

import pytest
from simplekv._compat import BytesIO, xrange
from simplekv.decorator import PrefixDecorator
from simplekv.crypt import HMACDecorator
from simplekv.idgen import UUIDDecorator, HashDecorator


class BasicStore(object):
    def test_store(self, store, key, value):
        store.put(key, value)

    def test_store_and_retrieve(self, store, key, value):
        store.put(key, value)
        assert store.get(key) == value

    def test_store_and_retrieve_filelike(self, store, key, value):
        store.put_file(key, BytesIO(value))
        assert store.get(key) == value

    def test_store_and_retrieve_overwrite(self, store, key, value, value2):
        store.put_file(key, BytesIO(value))
        assert store.get(key) == value

        store.put(key, value2)
        assert store.get(key) == value2

    def test_store_and_open(self, store, key, value):
        store.put_file(key, BytesIO(value))
        assert store.open(key).read() == value

    def test_open_incremental_read(self, store, key, long_value):
        store.put_file(key, BytesIO(long_value))
        ok = store.open(key)
        assert long_value[:3] == ok.read(3)
        assert long_value[3:5] == ok.read(2)
        assert long_value[5:8] == ok.read(3)

    def test_key_error_on_nonexistant_get(self, store, key):
        with pytest.raises(KeyError):
            store.get(key)

    def test_key_error_on_nonexistant_open(self, store, key):
        with pytest.raises(KeyError):
            store.open(key)

    def test_key_error_on_nonexistant_get_file(self, store, key):
        with pytest.raises(KeyError):
            store.get_file(key, BytesIO())

    def test_key_error_on_nonexistant_get_filename(self, store, key):
        with pytest.raises(KeyError):
            store.get_file(key, '/dev/null')

    def test_exception_on_invalid_key_get(self, store, invalid_key):
        with pytest.raises(ValueError):
            store.get(invalid_key)

    def test_exception_on_invalid_key_get_file(self, store, invalid_key):
        with pytest.raises(ValueError):
            store.get_file(invalid_key, '/dev/null')

    def test_exception_on_invalid_key_delete(self, store, invalid_key):
        with pytest.raises(ValueError):
            store.delete(invalid_key)

    def test_put_file(self, store, key, value):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmp.write(value)
            tmp.close()

            store.put_file(key, tmp.name)

            assert store.get(key) == value
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_put_opened_file(self, store, key, value):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(value)
            tmp.flush()

            store.put_file(key, open(tmp.name, 'rb'))

            assert store.get(key) == value

    def test_get_into_file(self, store, key, value):
        with TempDir() as tmpdir:
            store.put(key, value)
            out_filename = os.path.join(tmpdir, 'output')

            store.get_file(key, out_filename)

            assert open(out_filename, 'rb').read() == value

    def test_get_into_stream(self, store, key, value):
        store.put(key, value)

        output = BytesIO()

        store.get_file(key, output)
        assert output.getvalue() == value

    def test_put_return_value(self, store, key, value):
        assert key == store.put(key, value)

    def test_put_file_return_value(self, store, key, value):
        assert key == store.put_file(key, BytesIO(value))

    def test_put_filename_return_value(self, store, key, value):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmp.write(value)
            tmp.close()

            assert key == store.put_file(key, tmp.name)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_delete(self, store, key, value):
        store.put(key, value)

        assert value == store.get(key)

        store.delete(key)

        with pytest.raises(KeyError):
            store.get(key)

    def test_multiple_delete_fails_without_error(self, store, key, value):
        store.put(key, value)

        store.delete(key)
        store.delete(key)
        store.delete(key)

    def test_can_delete_key_that_never_exists(self, store, key):
        store.delete(key)

    def test_key_iterator(self, store, key, key2, value, value2):
        store.put(key, value)
        store.put(key2, value2)

        l = []
        for k in store.iter_keys():
            l.append(k)

        l.sort()

        assert l == sorted([key, key2])

    def test_keys(self, store, key, key2, value, value2):
        store.put(key, value)
        store.put(key2, value2)

        l = sorted(store.keys())

        assert l == sorted([key, key2])

    def test_has_key(self, store, key, key2, value):
        store.put(key, value)

        assert key in store
        assert key2 not in store

    def test_has_key_with_delete(self, store, key, value):
        assert key not in store

        store.put(key, value)
        assert key in store

        store.delete(key)
        assert key not in store

        store.put(key, value)
        assert key in store

    def test_get_with_delete(self, store, key, value):
        with pytest.raises(KeyError):
            store.get(key)

        store.put(key, value)
        store.get(key)

        store.delete(key)

        with pytest.raises(KeyError):
            store.get(key)

        store.put(key, value)
        store.get(key)

    def test_max_key_length(self, store, max_key, value):
        new_key = store.put(max_key, value)

        assert new_key == max_key
        assert value == store.get(max_key)

    def test_a_lot_of_puts(self, store, key, value):
        a_lot = 20

        for i in xrange(a_lot):
            key = key + '_{}'.format(i)
            store.put(key, value)


# small extra time added to account for variance
TTL_MARGIN = 1


class TTLStore(object):
    @pytest.fixture
    def ustore(self, store):
        return UUIDDecorator(store)

    @pytest.fixture(params=['hash', 'uuid', 'hmac', 'prefix'])
    def dstore(self, request, store, secret_key):
        if request.param == 'hash':
            return HashDecorator(store)
        elif request.param == 'uuid':
            return self.ustore(store)
        elif request.param == 'hmac':
            return HMACDecorator(secret_key, store)
        elif request.param == 'prefix':
            return PrefixDecorator('SaMpLe_PrEfIX', store)

    @pytest.fixture(params=[0.4, 1])
    def small_ttl(self, request):
        return request.param

    def test_put_with_negative_ttl_throws_error(self, store, key, value):
        with pytest.raises(ValueError):
            store.put(key, value, ttl_secs=-1)

    def test_put_with_non_numeric_ttl_throws_error(self, store, key, value):
        with pytest.raises(ValueError):
            store.put(key, value, ttl_secs='badttl')

    def test_put_with_ttl_argument(self, store, key, value, small_ttl):
        store.put(key, value, small_ttl)

        time.sleep(small_ttl + TTL_MARGIN)
        with pytest.raises(KeyError):
            store.get(key)

    def test_put_set_default(self, store, key, value, small_ttl):
        store.default_ttl_secs = small_ttl

        store.put(key, value)

        time.sleep(small_ttl + TTL_MARGIN)
        with pytest.raises(KeyError):
            store.get(key)

    def test_put_file_with_ttl_argument(self, store, key, value, small_ttl):
        store.put_file(key, BytesIO(value), small_ttl)

        time.sleep(small_ttl + TTL_MARGIN)
        with pytest.raises(KeyError):
            store.get(key)

    def test_put_file_set_default(self, store, key, value, small_ttl):
        store.default_ttl_secs = small_ttl

        store.put_file(key, BytesIO(value))

        time.sleep(small_ttl + TTL_MARGIN)
        with pytest.raises(KeyError):
            store.get(key)

    def test_uuid_decorator(self, ustore, value):
        key = ustore.put(None, value)

        assert key

    def test_advertises_ttl_features(self, store):
        assert store.ttl_support is True
        assert hasattr(store, 'ttl_support')
        assert getattr(store, 'ttl_support') is True

    def test_advertises_ttl_features_through_decorator(self, dstore):
        assert dstore.ttl_support is True
        assert hasattr(dstore, 'ttl_support')
        assert getattr(dstore, 'ttl_support') is True

    def test_can_pass_ttl_through_decorator(self, dstore, key, value):
        dstore.put(key, value, ttl_secs=10)
