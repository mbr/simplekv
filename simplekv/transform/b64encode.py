from .transformer import Transformer, TransformerPair
import io
import base64


def _bytesio_for_append(data):
    """
    Construct a io.BytesIO initialized to `data` for appending

    I.e., the write position is at the end
    """
    result = io.BytesIO(data)
    result.seek(len(data))
    return result


class Base64Encoder(Transformer):

    def __init__(self):
        # encode in chunks of 3
        self._buffer = io.BytesIO()

    def transform(self, data):
        self._buffer.write(data)
        to_consume = self._buffer.tell() - self._buffer.tell() % 3
        bufval = self._buffer.getvalue()
        retval = base64.b64encode(bufval[:to_consume])
        self._buffer = _bytesio_for_append(bufval[to_consume:])
        return retval

    def finalize(self):
        bufval = self._buffer.getvalue()
        del self._buffer
        return base64.b64encode(bufval)


class Base64Decoder(Transformer):

    def __init__(self):
        # decode in chunks of 4
        self._buffer = io.BytesIO()

    def transform(self, data):
        self._buffer.write(data)
        to_consume = self._buffer.tell() - self._buffer.tell() % 4
        bufval = self._buffer.getvalue()
        retval = base64.b64decode(bufval[:to_consume])
        self._buffer = _bytesio_for_append(bufval[to_consume:])
        return retval

    def finalize(self):
        bufval = self._buffer.getvalue()
        del self._buffer
        return base64.b64decode(bufval)


class B64Encode(TransformerPair):
    """
    Apply base64 encoding / decoding
    """

    def transformer(self):
        return Base64Encoder()

    def inverse(self):
        return Base64Decoder()

    def __str__(self):
        return 'B64Encode'
