import os
import re
import tempfile
import uuid

from simplekv.idgen import UUIDDecorator, HashDecorator

import pytest


UUID_REGEXP = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
)


class IDGen(object):
    @pytest.fixture(params=[
        'constant',
        'foo{}bar',
        '{}.jpeg',
        'prefix-{}.hello',
        'justprefix{}',
    ])
    def idgen_template(self, request):
        return request.param


class UUIDGen(IDGen):
    @pytest.fixture
    def uuidstore(self, store):
        return UUIDDecorator(store)

    @pytest.fixture
    def templated_uuidstore(self, store, idgen_template):
        return UUIDDecorator(store, idgen_template)

    def test_put_generates_uuid_form(self, uuidstore, value):
        key = uuidstore.put(None, value)
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

    def test_put_generates_valid_uuid(self, uuidstore, value):
        key = uuidstore.put(None, value)
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

    def test_templates_work(self, templated_uuidstore, value, idgen_template):
        key = templated_uuidstore.put(None, value)

        # should not be a valid UUID
        assert not UUID_REGEXP.match(key)


class HashGen(IDGen):
    @pytest.fixture
    def hashstore(self, store, hashfunc):
        return HashDecorator(store, hashfunc)

    @pytest.fixture
    def templated_hashstore(self, store, hashfunc, idgen_template):
        return HashDecorator(store, hashfunc, idgen_template)

    @pytest.fixture
    def validate_hash(self, hashfunc):
        hash_regexp = re.compile(r'^[0-9a-f]{{{}}}$'.format(
            hashfunc().digest_size * 2,
        ))

        return hash_regexp.match

    @pytest.fixture
    def value_hash(self, hashfunc, value):
        return hashfunc(value).hexdigest()

    def test_put_generates_valid_form(self, hashstore, validate_hash, value):
        key = hashstore.put(None, value)
        assert validate_hash(key)

    def test_put_file_generates_valid_form(self, hashstore, validate_hash):
        key = hashstore.put_file(None, open('/dev/null', 'rb'))
        assert validate_hash(key)

        # this is not correct according to our interface
        # /dev/null cannot be claimed by the hashstore
        # key2 = hashstore.put_file(None, '/dev/null')
        # assert validate_hash(key2)

    def test_put_generates_correct_hash(self, hashstore, value_hash, value):
        key = hashstore.put(None, value)

        assert value_hash == key

    def test_put_file_generates_correct_hash(
        self, hashstore, value_hash, value
    ):
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        try:
            tmpfile.write(value)
            tmpfile.close()
            with open(tmpfile.name, 'rb') as f:
                key = hashstore.put_file(None, f)
            assert key == value_hash

            key2 = hashstore.put_file(None, tmpfile.name)
            assert key2 == value_hash
        finally:
            if os.path.exists(tmpfile.name):
                os.unlink(tmpfile.name)

    def test_templates_work(
        self, templated_hashstore, value, idgen_template, value_hash
    ):
        key = templated_hashstore.put(None, value)

        assert idgen_template.format(value_hash) == key
