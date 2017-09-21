from simplekv.transform.adapter import ReadAdapter, WriteAdapter
import pytest
import io

from util import IdentityTransformer, IdentityTransformer2


def test_read_identity():
    testdata = b'sdj n02ht'
    # FIXME: remove:
    t = IdentityTransformer()
    assert t.transform(testdata) == testdata
    assert t.finalize() == b''
    file = io.BytesIO(testdata)
    ra = ReadAdapter(file, IdentityTransformer())
    assert ra.read() == testdata


def test_read_size_identity():
    testdata = b'sdj n02ht'
    file = io.BytesIO(testdata)
    ra = ReadAdapter(file, IdentityTransformer())
    assert (ra.read(2), ra.read(1), ra.read()) == (b'sd', b'j', b' n02ht')


def test_read_identity2():
    testdata = b'sdj n02ht'
    file = io.BytesIO(testdata)
    ra = ReadAdapter(file, IdentityTransformer2())
    assert ra.read() == testdata


def test_read_size_identity2():
    testdata = b'sdj n02ht'
    file = io.BytesIO(testdata)
    ra = ReadAdapter(file, IdentityTransformer2())
    assert (ra.read(2), ra.read(1), ra.read()) == (b'sd', b'j', b' n02ht')


def test_write_identity():
    testdata = b'sdj n02ht'
    file = io.BytesIO()
    wa = WriteAdapter(file, IdentityTransformer())
    wa.write(testdata)
    wa.close()
    assert file.getvalue() == testdata


def test_write_identity2():
    testdata = b'sdj n02ht'
    file = io.BytesIO()
    wa = WriteAdapter(file, IdentityTransformer2())
    wa.write(testdata)
    wa.close()
    assert file.getvalue() == testdata


def test_write_already_closed():
    file = io.BytesIO()
    wa = WriteAdapter(file, IdentityTransformer2())
    wa.write(b'a')
    wa.close()
    with pytest.raises(ValueError) as ex:
        wa.write(b'b')
    assert 'already closed' in str(ex)
