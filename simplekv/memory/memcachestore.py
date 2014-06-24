#!/usr/bin/env python
# coding=utf8

from io import BytesIO

from .. import KeyValueStore, TimeToLiveMixin, NOT_SET


class MemcacheStore(TimeToLiveMixin, KeyValueStore):
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

    def _put(self, key, data, ttl_secs):
        if ttl_secs == NOT_SET or ttl_secs is None:
            if not self.mc.set(key.encode('ascii'), data):
                if len(data) >= 1024 * 1023:
                    raise IOError('Failed to store data, probably too large. '\
                                  'memcached limit is 1M')
                raise IOError('Failed to store data')
        else:
            if not self.mc.set(key.encode('ascii'), data, ttl_secs):
                if len(data) >= 1024 * 1023:
                    raise IOError('Failed to store data, probably too large. '\
                                  'memcached limit is 1M')
                raise IOError('Failed to store data')

        return key

    def _put_file(self, key, file, ttl_secs):
        return self._put(key, file.read(), ttl_secs)

    def keys(self):
        raise IOError('Memcache does not support listing keys.')

    def iter_keys(self):
        raise IOError('Memcache does not support key iteration.')
