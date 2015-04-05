#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import BytesIO

from .. import KeyValueStore, TimeToLiveMixin, NOT_SET, FOREVER


class RedisStore(TimeToLiveMixin, KeyValueStore):
    """Uses a redis-database as the backend.

    :param redis: An instance of :py:class:`redis.StrictRedis`.
    """

    def __init__(self, redis):
        self.redis = redis

    def _delete(self, key):
        return self.redis.delete(key)

    def keys(self):
        return list(map(lambda b: b.decode(), self.redis.keys()))

    def iter_keys(self):
        return iter(self.keys())

    def _has_key(self, key):
        return self.redis.exists(key)

    def _get(self, key):
        val = self.redis.get(key)

        if val is None:
            raise KeyError(key)
        return val

    def _get_file(self, key, file):
        file.write(self._get(key))

    def _open(self, key):
        return BytesIO(self._get(key))

    def _put(self, key, value, ttl_secs):
        if ttl_secs in (NOT_SET, FOREVER):
            # if we do not care about ttl, just use set
            # in redis, using SET will also clear the timeout
            # note that this assumes that there is no way in redis
            # to set a default timeout on keys
            self.redis.set(key, value)
        else:
            ittl = None
            try:
                ittl = int(ttl_secs)
            except ValueError:
                pass  # let it blow up further down

            if ittl == ttl_secs:
                self.redis.setex(key, ittl, value)
            else:
                self.redis.psetex(key, int(ttl_secs * 1000), value)

        return key

    def _put_file(self, key, file, ttl_secs):
        self._put(key, file.read(), ttl_secs)
        return key
