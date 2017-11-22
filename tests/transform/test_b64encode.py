# coding=utf-8
from simplekv.transform.b64encode import (
    Base64Encoder, Base64Decoder, B64Encode,
)
from simplekv.transform.transformer import Pipe
from base64 import b64encode
import pytest


# make sure to include payload sizes around the base64 blockk length
# of 3 bytes in the test, as well as the empty string as special case.
# Thus, use a new test fixture instead of the 'value' one

@pytest.fixture(params=[b'', b'X', b'XY', b'XYZ', b'XYZW'])
def testdata(request):
    return request.param


def test_roundtrip(testdata):
    pair = B64Encode()
    p = Pipe([pair.transformer(), pair.inverse()])
    assert p.transform(testdata) + p.finalize() == testdata


def test_str():
    pair = B64Encode()
    assert str(pair) == 'B64Encode'


def test_encoder_singlebytes(testdata):
    enc = Base64Encoder()
    output = b''
    for i in range(len(testdata)):
        output += enc.transform(testdata[i:i + 1])
    output += enc.finalize()
    assert output == b64encode(testdata)


def test_decoder_singlebytes(testdata):
    dec = Base64Decoder()
    output = b''
    enc_testdata = b64encode(testdata)
    for i in range(len(enc_testdata)):
        output += dec.transform(enc_testdata[i:i + 1])
    output += dec.finalize()
    assert output == testdata
