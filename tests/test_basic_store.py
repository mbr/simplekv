#!/usr/bin/env python
# coding=utf8

from StringIO import StringIO
import os
import shutil
import tempfile

import pytest


def test_store(store):
    store.put('key1', 'data1')


def test_store_and_retrieve(store):
    v = 'data1'
    k = 'key1'
    store.put(k, v)
    assert store.get(k) == v


def test_store_and_retrieve_filelike(store):
    v = 'data1'
    k = 'key1'

    store.put_file(k, StringIO(v))
    assert store.get(k) == v


def test_store_and_retrieve_overwrite(store):
    v = 'data1'
    v2 = 'data2'

    k = 'key1'

    store.put_file(k, StringIO(v))
    assert store.get(k) == v

    store.put(k, v2)
    assert store.get(k) == v2


def test_store_and_open(store):
    v = 'data1'
    k = 'key1'

    store.put_file(k, StringIO(v))
    assert store.open(k).read() == v


def test_open_incremental_read(store):
    v = 'data_abc'
    k = 'key1'

    store.put_file(k, StringIO(v))
    ok = store.open(k)
    assert v[:3] == ok.read(3)
    assert v[3:5] == ok.read(2)
    assert v[5:8] == ok.read(3)


def test_key_error_on_nonexistant_get(store):
    with pytest.raises(KeyError):
        store.get('doesnotexist')


def test_key_error_on_nonexistant_open(store):
    with pytest.raises(KeyError):
        store.open('doesnotexist')


def test_exception_on_invalid_key_get(store):
    with pytest.raises(ValueError):
        store.get(u'ä')

    with pytest.raises(ValueError):
        store.get('/')

    with pytest.raises(ValueError):
        store.get('\x00')

    with pytest.raises(ValueError):
        store.get('*')

    with pytest.raises(ValueError):
        store.get('')


def test_exception_on_invalid_key_get_file(store):
    with pytest.raises(ValueError):
        store.get_file(u'ä', '/dev/null')

    with pytest.raises(ValueError):
        store.get_file('/', '/dev/null')

    with pytest.raises(ValueError):
        store.get_file('\x00', '/dev/null')

    with pytest.raises(ValueError):
        store.get_file('*', '/dev/null')

    with pytest.raises(ValueError):
        store.get_file('', '/dev/null')


def test_exception_on_invalid_key_delete(store):
    with pytest.raises(ValueError):
        store.delete(u'ä')

    with pytest.raises(ValueError):
        store.delete('/')

    with pytest.raises(ValueError):
        store.delete('\x00')

    with pytest.raises(ValueError):
        store.delete('*')

    with pytest.raises(ValueError):
        store.delete('')


def test_put_file(store):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        k = 'filekey1'
        v = 'somedata'
        tmp.write(v)
        tmp.close()

        store.put_file(k, tmp.name)

        assert store.get(k) == v
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


def test_put_opened_file(store):
    with tempfile.NamedTemporaryFile() as tmp:
        k = 'filekey2'
        v = 'somedata2'
        tmp.write(v)
        tmp.flush()

        store.put_file(k, open(tmp.name, 'rb'))

        assert store.get(k) == v


def test_get_into_file(store):
    tmpdir = tempfile.mkdtemp()
    try:
        k = 'asdf'
        v = '123'
        store.put(k, v)
        out_filename = os.path.join(tmpdir, 'output')

        store.get_file(k, out_filename)

        assert open(out_filename, 'rb').read() == v
    finally:
        shutil.rmtree(tmpdir)


def test_get_into_stream(store):
    k = 'mykey123'
    v = 'another_value'
    store.put(k, v)

    output = StringIO()

    store.get_file(k, output)
    assert output.getvalue() == v


def test_get_nonexistant(store):
    with pytest.raises(KeyError):
        store.get('nonexistantkey')


def test_get_file_nonexistant(store):
    with pytest.raises(KeyError):
        store.get_file('nonexistantkey', StringIO())


def test_get_filename_nonexistant(store):
    with pytest.raises(KeyError):
        store.get_file('nonexistantkey', '/dev/null')


def test_put_return_value(store):
    k = 'mykey456'
    v = 'some_val'

    rv = store.put(k, v)

    assert k == rv


def test_put_file_return_value(store):
    k = 'rvkey12'
    v = 'some_val'

    rv = store.put_file(k, StringIO(v))

    assert k == rv


def test_put_filename_return_value(store):
    k = 'filenamekey1'
    v = 'some_val'

    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        tmp.write(v)
        tmp.close()

        rv = store.put_file(k, tmp.name)

        assert rv == k
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


def test_delete(store):
    k = 'key_not_long_this_world'
    v = 'worldy_value'

    store.put(k, v)

    assert v == store.get(k)

    store.delete(k)

    with pytest.raises(KeyError):
        store.get(k)


def test_multiple_delete_fails_without_error(store):
    k = 'd1'
    v = 'v1'

    store.put(k, v)

    store.delete(k)
    store.delete(k)
    store.delete(k)


def test_can_delete_key_that_never_exists(store):
    store.delete('never_ever_existed')


def test_key_iterator(store):
    store.put('key1', 'someval')
    store.put('key2', 'someval2')
    store.put('key3', 'someval3')

    l = []
    for k in store.iter_keys():
        l.append(k)

    l.sort()

    assert l == ['key1', 'key2', 'key3']


def test_keys(store):
    store.put('key1', 'someval')
    store.put('key2', 'someval2')
    store.put('key3', 'someval3')

    l = store.keys()
    l.sort()

    assert l == ['key1', 'key2', 'key3']


def test_has_key(store):
    k = 'keya'
    k2 = 'key2'
    store.put(k, 'vala')

    assert k in store
    assert k2 not in store


def test_has_key_with_delete(store):
    k = 'keyb'

    assert k not in store

    store.put(k, 'valb')
    assert k in store

    store.delete(k)
    assert k not in store

    store.put(k, 'valc')
    assert k in store


def test_get_with_delete(store):
    k = 'keyb'

    with pytest.raises(KeyError):
        store.get(k)

    store.put(k, 'valb')
    store.get(k)

    store.delete(k)

    with pytest.raises(KeyError):
        store.get(k)

    store.put(k, 'valc')
    store.get(k)


def test_max_key_length(store):
    key = 'a' * 250
    val = '1234'

    new_key = store.put(key, val)

    assert new_key == key
    assert val == store.get(key)


def test_key_special_characters(store):
    key = """'!"`#$%&'()+,-.<=>?@[]^_{}~'"""

    val = '1234'
    new_key = store.put(key, val)

    assert new_key == key
    assert val == store.get(key)


def test_keys_with_whitespace_rejected(store):
    key = 'an invalid key'

    with pytest.raises(ValueError):
        store.put(key, 'foo')


def test_a_lot_of_puts(store):
    a_lot = 20

    for i in xrange(a_lot):
        key = 'this_is_key_%d_of_%d' % (i, a_lot)
        val = os.urandom(512)
        store.put(key, val)
