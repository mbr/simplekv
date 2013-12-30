#!/usr/bin/env python
# coding=utf8

from io import BytesIO

from .. import KeyValueStore


class DictStore(KeyValueStore):
    """Store data in a dictionary.

    This store uses a dictionary as the backend for storing, its implementation
    is straightforward. The dictionary containing all data is available as `d`.
    """
    def __init__(self, d=None):
        self.d = d or {}

    def _delete(self, key):
        self.d.pop(key, None)

    def _has_key(self, key):
        return key in self.d

    def _open(self, key):
        return BytesIO(self.d[key])

    def _put_file(self, key, file):
        self.d[key] = file.read()
        return key

    def iter_keys(self):
        return iter(self.d)
