#!/usr/bin/env python
# coding=utf8

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .. import KeyValueStore


class MemcacheStore(KeyValueStore):
    def __contains__(self, key):
        try:
            return key in self.mc
        except TypeError:
            raise IOError('memcache implementation does not support '\
                          '__contains__')

    def __init__(self, mc):
        self.mc = mc

    def _delete(self, key):
        self.mc.delete(key)

    def _get(self, key):
        rv = self.mc.get(key)
        if None == rv:
            raise KeyError(key)
        return rv

    def _get_file(self, key, file):
        file.write(self._get(key))

    def _open(self, key):
        return StringIO(self._get(key))

    def _put(self, key, data):
        self.mc.set(key, data)
        return key

    def _put_file(self, key, file):
        self.mc.set(key, file.read())
        return key

    def keys(self):
        raise IOError('Memcache does not support listing keys.')

    def iter_keys(self):
        raise IOError('Memcache does not support key iteration.')
