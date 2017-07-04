# coding: utf8
import hashlib

import pytest


@pytest.fixture(params=['sha1', 'sha256', 'md5'])
def hashfunc(request):
    return getattr(hashlib, request.param)


@pytest.fixture(params=[b'secret_key_a', b'\x12\x00\x12test'])
def secret_key(request):
    return request.param


# values are short payloads to store
@pytest.fixture(params=[b'a_short_value', b'another_short_value'])
def value(request):
    return request.param


@pytest.fixture(params=[b'the_other_value', b'other_value_2'])
def value2(request):
    return request.param


@pytest.fixture(params=[u'the_other_value', u'othäöü_valਊਏਐਓਔਕਖਗue_2'])
def unicode_value(request):
    return request.param


@pytest.fixture(params=[b'a_long_value' * 4 * 1024])
def long_value(request):
    return request.param


# keys are always strings. only ascii chars are allowed
@pytest.fixture(params=[u'short_key', u'different_key',
                        u"""'!"`#$%&'()+,-.<=>?@[]^_{}~'"""])
def key(request):
    return request.param


@pytest.fixture(params=[u'key_number_2', u'and_again_a_second_key'])
def key2(request):
    return request.param


@pytest.fixture(params=[u'ä', u'/', u'\x00', u'*', u'',
                        u'no whitespace allowed'])
def invalid_key(request):
    return request.param


@pytest.fixture(params=[b'short_key', b'different_key',
                        b"""'!"`#$%&'()+,-.<=>?@[]^_{}~'"""])
def bytestring_key(request):
    return request.param


# maximum length key
@pytest.fixture(params=[u'a' * 250, u'b' * 250])
def max_key(request):
    return request.param


# Test class to derive from to get test fixtures for the extended keyspace
class ExtendedKeyspaceTests:
    @pytest.fixture(params=[u'short ke/y', u'short_key', u'spaces  in key',
                            u"""'!"`#$%&'()+,-.<=>?@[]^_{}~/'"""])
    def key(self, request):
        return request.param

    @pytest.fixture(params=[u'key_number/2 with space',
                            u'and_again_a_second_key'])
    def key2(self, request):
        return request.param

    @pytest.fixture(params=[u'ä', u'/', u'\x00', u'*', u''])
    def invalid_key(self, request):
        return request.param
