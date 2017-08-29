# coding=utf8

"""
Implement the transformer interface for gzip compression
"""

import zlib
from .transformer import Transformer, TransformerPair


class CompressingTransformer(Transformer):

    def __init__(self, level, wbits, memlevel):
        self.cobj = zlib.compressobj(level, zlib.DEFLATED, wbits,
                                     memlevel, zlib.Z_DEFAULT_STRATEGY)

    def transform(self, data):
        return self.cobj.compress(data)

    def finalize(self):
        return self.cobj.flush()


class DecompressingTransformer(Transformer):

    def __init__(self, wbits):
        self.dobj = zlib.decompressobj(wbits)

    def transform(self, data):
        result = [self.dobj.decompress(data)]
        while self.dobj.unconsumed_tail:
            # hard to get coverage for this, but that's how one should use
            # it according to docs ...
            result.append(self.dobj.decompress(self.dobj.unconsumed_tail))
        return b''.join(result)

    def finalize(self):
        assert not self.dobj.unconsumed_tail
        result = self.dobj.flush()
        if self.dobj.unused_data != b'':
            raise ValueError("Unused data found after decompression completed")
        return result


class Gzip(TransformerPair):
    """
    Apply gzip compression / decompression

    :param level: see zlib.compress / gzip.GZipFile
    :param memlevel: see `memlevel` of zlib.compress
    """

    def __init__(self, level=9, memlevel=zlib.DEF_MEM_LEVEL):
        self.level = level
        self.memlevel = memlevel

    def transformer(self):
        # wbit = 31 writes the gzip header and trailer
        return CompressingTransformer(self.level, 31, self.memlevel)

    def inverse(self):
        # wbit = 47 accepts the gzip header / trailer
        return DecompressingTransformer(47)

    def __str__(self):
        return 'Gzip'
