import os
import re
import tempfile
import uuid

from simplekv.idgen import UUIDDecorator, HashDecorator

import pytest


UUID_REGEXP = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
)


class UUIDGen(object):
    @pytest.fixture
    def uuidstore(self, store):
        return UUIDDecorator(store)

    def test_put_generates_uuid_form(self, uuidstore):
        key = uuidstore.put(None, 'some_data')
        assert UUID_REGEXP.match(key)

    def test_put_file_generates_uuid_form(self, uuidstore):
        key = uuidstore.put_file(None, open('/dev/null', 'rb'))
        assert UUID_REGEXP.match(key)

        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.close()
            key2 = uuidstore.put_file(None, tmpfile.name)
            assert UUID_REGEXP.match(key2)
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)

    def test_put_generates_valid_uuid(self, uuidstore):
        key = uuidstore.put(None, 'some_data')
        uuid.UUID(hex=key)

    def test_put_file_generates_valid_uuid(self, uuidstore):
        key = uuidstore.put_file(None, open('/dev/null', 'rb'))
        uuid.UUID(hex=key)

        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.close()
            key2 = uuidstore.put_file(None, tmpfile.name)
            uuid.UUID(hex=key2)
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)


class HashGen(object):
    @pytest.fixture
    def hashstore(self, store, hashfunc):
        return HashDecorator(store, hashfunc)

    @pytest.fixture
    def validate_hash(self, hashfunc):
        hash_regexp = re.compile(r'^[0-9a-f]{{{}}}$'.format(
            hashfunc().digest_size * 2,
        ))

        return hash_regexp.match

    def test_put_generates_valid_form(self, hashstore, validate_hash):
        key = hashstore.put(None, 'some_data')
        assert validate_hash(key)

    def test_put_file_generates_valid_form(self, hashstore, validate_hash):
        key = hashstore.put_file(None, open('/dev/null', 'rb'))
        assert validate_hash(key)

        # this is not correct according to our interface
        # /dev/null cannot be claimed by the hashstore
        # key2 = hashstore.put_file(None, '/dev/null')
        # assert validate_hash(key2)

    def test_put_generates_correct_hash(self, hashstore, hashfunc):
        data = 'abcdXefg'
        key = hashstore.put(None, data)

        assert hashfunc(data).hexdigest() == key

    def test_put_file_generates_correct_hash(self, hashstore, hashfunc):
        data = '!bcdXefQ'
        h = hashfunc(data).hexdigest()

        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.write(data)
            tmpfile.close()
            with open(tmpfile.name, 'rb') as f:
                key = hashstore.put_file(None, f)
            assert key == h

            key2 = hashstore.put_file(None, tmpfile.name)
            assert key2 == h
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)
