#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .. import KeyValueStore


class RedisStore(KeyValueStore):
    """Uses a redis-database as the backend.

    :param redis: An instance of :py:class:`redis.StrictRedis`.
    """

    def __init__(self, redis):
        self.redis = redis

    def _delete(self, key):
        return self.redis.delete(key)

    def keys(self):
        return self.redis.keys()

    def iter_keys(self):
        return iter(self.keys())

    def _has_key(self, key):
        return self.redis.exists(key)

    def _get(self, key):
        val = self.redis.get(key)

        if val == None:
            raise KeyError(key)
        return val

    def _get_file(self, key, file):
        file.write(self._get(key))

    def _open(self, key):
        return StringIO(self._get(key))

    def _put(self, key, value):
        self.redis.set(key, value)
        return key

    def _put_file(self, key, file):
        self._put(key, file.read())
        return key
