#!/usr/bin/env python
# coding=utf8

import os

from . import KeyValueStorage

class FilesystemStore(KeyValueStorage):
    def __init__(self, root):
        self.root = root
        self.bufsize = 2 ** 32 - 1

    def _build_filename(self, key):
        return os.path.join(self.root, key)

    def _put_data(self, key, data):
        with file(self._build_filename(key), 'wb') as f:
            f.write(data)

    def _put_readable(self, key, source):
        bufsize = self.bufsize
        with file(self._build_filename(key), 'wb') as f:
            while True:
                buf = source.read(bufsize)
                f.write(buf)
                if len(buf) < bufsize:
                    break
