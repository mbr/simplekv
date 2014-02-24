import hashlib

from six import b

import pytest


@pytest.fixture(params=['sha1', 'sha256', 'md5'])
def hashfunc(request):
    return getattr(hashlib, request.param)


@pytest.fixture(params=['secret_key_a', '\x12\x00\x12test'])
def secret_key(request):
    return request.param


# values are short payloads to store
@pytest.fixture(params=[b('a_short_value'), b('another_short_value')])
def value(request):
    return request.param


@pytest.fixture(params=[b('short_key'), b('different_key')])
def key(request):
    return request.param
