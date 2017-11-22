# coding=utf-8
from simplekv.transform.gzip import Gzip
from simplekv.transform.transformer import Pipe
from util import gen_random_bytes
from gzip import GzipFile
import io
import pytest


def _compress(data):
    # use gzip.GzipFile to compress data
    buffer = io.BytesIO()
    gfile = GzipFile(fileobj=buffer, mode='w')
    gfile.write(data)
    gfile.close()
    return buffer.getvalue()


def _decompress(data):
    # use gzip.GzipFile to decompress data
    gfile = GzipFile(fileobj=io.BytesIO(data), mode='r')
    return gfile.read()


def test_compress_gzip(value):
    p = Gzip()
    gzipper = p.transformer()
    output = gzipper.transform(value) + gzipper.finalize()
    assert _decompress(output) == value


def test_decompress_gzip(value):
    p = Gzip()
    gunzipper = p.inverse()
    output = gunzipper.transform(_compress(value)) + gunzipper.finalize()
    assert output == value


def test_roundtrip(value):
    p = Gzip()
    pipe = Pipe([p.transformer(), p.inverse()])
    output = pipe.transform(value) + pipe.finalize()
    assert output == value


def test_unused_data_raises():
    p = Gzip()
    gunzipper = p.inverse()
    teststring = b'lrigjoij t'
    with pytest.raises(ValueError) as ex:
        (gunzipper.transform(_compress(teststring) + b'additional_data') +
         gunzipper.finalize())
    assert 'Unused data' in str(ex.value)


def test_decompress_random_string():
    # decompressing large data may need several passes using
    # zlib.Decompress.unconsumed_tail
    teststring = gen_random_bytes(10000)
    compressed = _compress(teststring)
    unzip = Gzip(memlevel=1).inverse()
    assert unzip.transform(compressed) + unzip.finalize() == teststring
