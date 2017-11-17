# coding=utf-8
from simplekv.transform.transformer import Transformer, TransformerPair
import io
import random


def gen_random_bytes(n):
    # generate random data for testing
    return bytes([random.randint(0, 255) for _ in range(n)])


class IdentityTransformer(Transformer):

    def transform(self, data):
        return data

    def finalize(self):
        return b''


class IdentityTransformer2(Transformer):
    """
    buffer eveything until finalize
    """

    def __init__(self):
        self._buffer = io.BytesIO()

    def transform(self, data):
        self._buffer.write(data)
        return b''

    def finalize(self):
        return self._buffer.getvalue()


class ReverseTransformer(Transformer):
    def __init__(self):
        self._buffer = io.BytesIO()

    def transform(self, data):
        self._buffer.write(data)
        return b''

    def finalize(self):
        return self._buffer.getvalue()[::-1]


class ReverseTransformerPair(TransformerPair):

    def transformer(self):
        return ReverseTransformer()

    def inverse(self):
        return ReverseTransformer()
