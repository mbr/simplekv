# coding=utf8

"""
Apply a transformer to an underlying file and expose a file-like interface
"""

import io

_DEFAULT_CHUNK_SIZE = 1 << 16  # 65k


class ReadAdapter(object):
    """Read data from an underlying file, transform it, and provide it via `read`
    """

    def __init__(self, file, transformer, chunk_size=_DEFAULT_CHUNK_SIZE):
        self.transformer = transformer
        self.chunk_size = chunk_size
        self.file = file
        # buffer transformed data to be returned by `read`
        self._buffer = io.BytesIO()
        # has self.transformer.finalize been called
        self._finalized = False

    def read(self, size=-1):
        """
        Read transformed data

        :param size: the number of transformed bytes to read; a negative value
          means to read until end-of-file.
        :return: the transformed bytes. Empty if end-of-file has been reached.
        """
        results = []
        while size != 0:
            result_part = self._buffer.read(size)
            if not result_part:
                if self._finalized:
                    break
                # reached the end of self._buffer. Re-fill
                # it by reading from the underlying file.
                data = self.file.read(self.chunk_size)
                if not data:
                    # eof of underlying file: finalize transformer
                    self._buffer = io.BytesIO(self.transformer.finalize())
                    self._finalized = True
                else:
                    self._buffer = io.BytesIO(self.transformer.transform(data))
            else:
                size -= len(result_part)
                results.append(result_part)
        return b''.join(results)


class WriteAdapter(object):
    """
    Accept data via `write`, and write transformed data to an underlying file

    IMPORTANT: you must call `close` (before closing the unerlying file)
    to ensure that any buffered data is written to the underlying file.

    :param file: file-like object with a `write` method to write the
      transformed data to
    :param transformer: a Transformer to apply to the data passed to `write`,
      before writing it to `file`
    """

    def __init__(self, file, transformer):
        self.transformer = transformer
        self.file = file
        self._closed = False

    def write(self, data):
        """
        Transform `data` and write the transformed data to the underlying file.

        :return: the number of transformed bytes written
        """
        if self._closed:
            raise ValueError("already closed")
        transformed = self.transformer.transform(data)
        self.file.write(transformed)
        return len(transformed)

    def close(self):
        """
        Write any pending bytes to the underlying file

        Note that this does not close the underlying file.
        """
        data = self.transformer.finalize()
        self.file.write(data)
        self._closed = True
