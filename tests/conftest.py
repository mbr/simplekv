import hashlib

import pytest


@pytest.fixture(params=['sha1', 'sha256', 'md5'])
def hashfunc(request):
    return getattr(hashlib, request.param)


@pytest.fixture(params=['secret_key_a', '\x12\x00\x12test'])
def secret_key(request):
    return request.param
