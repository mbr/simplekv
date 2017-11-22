# coding=utf-8
from simplekv.transform.transformer import Pipe, PipeTransformerPair
from simplekv.transform.gzip import Gzip
from simplekv.transform.b64encode import B64Encode
from util import ReverseTransformer, ReverseTransformerPair


def test_pipe(value):
    p = Pipe([ReverseTransformer(), ReverseTransformer()])
    output = p.transform(value) + p.finalize()
    assert output == value


def test_pipe_pair(value):
    p = PipeTransformerPair(
        [ReverseTransformerPair(), ReverseTransformerPair()]
    )

    trafo = p.transformer()
    output = trafo.transform(value) + trafo.finalize()
    assert output == value

    inverse = p.inverse()
    output = inverse.transform(value) + inverse.finalize()
    assert output == value


def test_pipe_pair_gzip(value):
    p = PipeTransformerPair([Gzip(), Gzip()])

    trafo = p.transformer()
    double_gzip = trafo.transform(value) + trafo.finalize()

    inverse = p.inverse()
    roundtrip = inverse.transform(double_gzip) + inverse.finalize()
    assert roundtrip == value


def test_pipe_pair_gzip_b64(value):
    p = PipeTransformerPair([Gzip(), B64Encode()])

    trafo = p.transformer()
    transformed = trafo.transform(value) + trafo.finalize()

    inverse = p.inverse()
    restored = inverse.transform(transformed) + inverse.finalize()
    assert restored == value
