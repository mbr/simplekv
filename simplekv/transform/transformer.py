# coding=utf8


class Transformer(object):
    """
    Transform a byte-stream to another byte-stream
    """

    def transform(self, data):
        """
        Apply the transformation to the given parameter.

        Return as many bytes as possible of the transformed
        sequence (although may return nothing and buffer everything,
        depending on the operation)

        :param bytes: the bytes to transform
        :return: the transformed bytes (may be empty)
        """

    def finalize(self):
        """
        Emit any pending output at the end of the input stream.

        This is called once the end of the input sequence fed
        to :meth:`Transform.transform` has been reached.

        It is illegal to call :meth:`Transform.transform` after
        :meth:`Transform.finalize`.

        :return: the transformed bytes (may be empty)
        """


class TransformerPair(object):
    """
    Abstract factory for a transformer and its inverse
    """

    def transformer(self):
        """
        Build a transformer

        :return: a :class:`~.Transformer`
        """

    def inverse(self):
        """
        Build the reverse transformer

        The returned transformer is the inverse of
        the transformer returned by :meth:`TransformerPair.transformer`

        :return: a :class:`~.Transformer`
        """


class Pipe(Transformer):
    """
    Apply a sequence of transformers
    """

    def __init__(self, transformers):
        self.transformers = transformers

    def transform(self, data):
        for trafo in self.transformers:
            data = trafo.transform(data)
        return data

    def finalize(self):
        bytes = b''

        for trafo in self.transformers:
            if bytes:
                bytes = trafo.transform(bytes)
            bytes += trafo.finalize()
        return bytes


class PipeTransformerPair(TransformerPair):
    """
    Apply a sequence of TransformerPairs
    """

    def __init__(self, transformer_pairs):
        self.transformer_pairs = tuple(transformer_pairs)

    def transformer(self):
        return Pipe([tp.transformer() for tp in self.transformer_pairs])

    def inverse(self):
        return Pipe([tp.inverse() for tp in self.transformer_pairs[::-1]])

    def __str__(self):
        return ' | '.join(str(tp) for tp in self.transformer_pairs)
