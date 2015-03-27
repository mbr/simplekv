#!/usr/bin/env python
# coding=utf8

from io import BytesIO

from .. import KeyValueStore, TimeToLiveMixin, FOREVER, NOT_SET


class MemcacheStore(TimeToLiveMixin, KeyValueStore):
    def __contains__(self, key):
        try:
            return key in self.mc
        except TypeError:
            raise IOError('memcache implementation does not support '
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
        time = 0  # default is never expire, there is no explicit "not set"
                  # in memcached. both, pylibmc and python-memcached use
                  # 0 as the default value for an unset time
        if ttl_secs not in (NOT_SET, FOREVER):
            if ttl_secs == 0:
                # note that 0 in simplekv's terms means "expire after 0 secs",
                # that is immediately. memcached understands this as "forever"
                # a (slightly cringeworthy) workaround here is setting a
                # short expiration time

                time = 1
            else:
                # memcached only supports integer ttl in its protocol
                time = int(ttl_secs)

        if not self.mc.set(key.encode('ascii'), data, time=time):
            if len(data) >= 1024 * 1023:
                raise IOError('Failed to store data, probably too large. '
                              'memcached limit is 1M')
            raise IOError('Failed to store data')

        return key

    def _put_file(self, key, file, ttl_secs):
        return self._put(key, file.read(), ttl_secs)

    def keys(self):
        raise IOError('Memcache does not support listing keys.')

    def iter_keys(self):
        raise IOError('Memcache does not support key iteration.')
