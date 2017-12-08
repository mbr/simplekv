# coding=utf-8
from simplekv.transform.adapter import ReadAdapter, WriteAdapter
import pytest
import io

from util import IdentityTransformer, IdentityTransformer2


def test_read_identity(value):
    t = IdentityTransformer()
    assert t.transform(value) == value
    assert t.finalize() == b''
    file = io.BytesIO(value)
    ra = ReadAdapter(file, IdentityTransformer())
    assert ra.read() == value


def test_read_size_identity(value):
    file = io.BytesIO(value)
    ra = ReadAdapter(file, IdentityTransformer())
    assert (ra.read(2), ra.read(1), ra.read()) == (value[:2], value[2:3], value[3:])


def test_read_identity2(value):
    file = io.BytesIO(value)
    ra = ReadAdapter(file, IdentityTransformer2())
    assert ra.read() == value


def test_read_size_identity2(value):
    file = io.BytesIO(value)
    ra = ReadAdapter(file, IdentityTransformer2())
    assert (ra.read(2), ra.read(1), ra.read()) == (value[:2], value[2:3], value[3:])


def test_read_iobase_interface():
    file = io.BytesIO(b'data')
    ra = ReadAdapter(file, IdentityTransformer())
    assert ra.readable()
    assert not ra.seekable()
    assert not ra.writable()
    assert not ra.isatty()
    assert not ra.closed
    assert not file.closed
    ra.close()
    assert ra.closed
    assert file.closed
    with pytest.raises(ValueError) as ex:
        ra.read()
    assert 'already closed' in str(ex.value)


def test_write_identity(value):
    file = io.BytesIO()
    wa = WriteAdapter(file, IdentityTransformer())
    wa.write(value)
    wa.close()
    assert file.getvalue() == value


def test_write_identity2(value):
    file = io.BytesIO()
    wa = WriteAdapter(file, IdentityTransformer2())
    wa.write(value)
    wa.close()
    assert file.getvalue() == value


def test_write_already_closed():
    file = io.BytesIO()
    wa = WriteAdapter(file, IdentityTransformer2())
    wa.write(b'a')
    wa.close()
    with pytest.raises(ValueError) as ex:
        wa.write(b'b')
    assert 'already closed' in str(ex)
