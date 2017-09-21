from simplekv.transform.transformer import Pipe, PipeTransformerPair
from simplekv.transform.gzip import Gzip
from simplekv.transform.b64encode import B64Encode
from util import ReverseTransformer, ReverseTransformerPair


def test_pipe():
    p = Pipe([ReverseTransformer(), ReverseTransformer()])
    testdata = b'lfig 8ijg'
    output = p.transform(testdata) + p.finalize()
    assert output == testdata


def test_pipe_pair():
    p = PipeTransformerPair([ReverseTransformerPair(), ReverseTransformerPair()])
    testdata = b'lfig 8ijg'

    trafo = p.transformer()
    output = trafo.transform(testdata) + trafo.finalize()
    assert output == testdata

    inverse = p.inverse()
    output = inverse.transform(testdata) + inverse.finalize()
    assert output == testdata


def test_pipe_pair_gzip():
    p = PipeTransformerPair([Gzip(), Gzip()])
    testdata = b'lfig 8ijg'

    trafo = p.transformer()
    double_gzip = trafo.transform(testdata) + trafo.finalize()

    inverse = p.inverse()
    roundtrip = inverse.transform(double_gzip) + inverse.finalize()
    assert roundtrip == testdata


def test_pipe_pair_gzip_b64():
    p = PipeTransformerPair([Gzip(), B64Encode()])
    testdata = b'lfig 8ijg'

    trafo = p.transformer()
    transformed = trafo.transform(testdata) + trafo.finalize()

    inverse = p.inverse()
    restored = inverse.transform(transformed) + inverse.finalize()
    assert restored == testdata
