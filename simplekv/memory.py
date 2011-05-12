#!/usr/bin/env python
# coding=utf8

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from . import KeyValueStorage


class DictStore(KeyValueStorage):
    def __init__(self, d=None):
        self.d = d or {}

    def _open(self, key):
        return StringIO(self.d[key])

    def _put_file(self, key, file):
        self.d[key] = file.read()
