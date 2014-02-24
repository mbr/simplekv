#!/usr/bin/env python
# coding=utf8

from io import BytesIO

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
        if not self.mc.delete(key.encode('ascii')):
            raise IOError('Error deleting key')

    def _get(self, key):
        rv = self.mc.get(key.encode('ascii'))
        if None == rv:
            raise KeyError(key)
        return rv

    def _get_file(self, key, file):
        file.write(self._get(key))

    def _open(self, key):
        return BytesIO(self._get(key))

    def _put(self, key, data):
        if not self.mc.set(key.encode('ascii'), data):
            if len(data) >= 1024 * 1023:
                raise IOError('Failed to store data, probably too large. '\
                              'memcached limit is 1M')
            raise IOError('Failed to store data')
        return key

    def _put_file(self, key, file):
        return self._put(key, file.read())

    def keys(self):
        raise IOError('Memcache does not support listing keys.')

    def iter_keys(self):
        raise IOError('Memcache does not support key iteration.')
