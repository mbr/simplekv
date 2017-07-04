#!/usr/bin/env python
# coding=utf8

from io import BytesIO
from .._compat import ifilter

from .. import KeyValueStore, CopyMixin


class DictStore(KeyValueStore, CopyMixin):
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

    def _copy(self, source, dest):
        self.d[dest] = self.d[source]

    def _put_file(self, key, file):
        self.d[key] = file.read()
        return key

    def iter_keys(self, prefix=u""):
        # We need the copy here so the user can modify the store while iterating through the keys
        return ifilter(lambda k: k.startswith(prefix), iter(self.d.copy()))
