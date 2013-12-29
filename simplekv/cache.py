#!/usr/bin/env python
# coding=utf8

from .decorator import StoreDecorator


class CacheDecorator(StoreDecorator):
    """Write-through cache decorator.

    Can combine two :class:`~simplekv.KeyValueStore` instances into a single
    caching :class:`~simplekv.KeyValueStore`. On a data-read request, the cache
    will be consulted first, if there is a cache miss or an error, data will be
    read from the backing store. Any retrieved value will be stored in the
    cache before being forward to the client.

    Write, key-iteration and delete requests will be passed on straight to the
    backing store. After their completion, the cache will be updated.

    No cache maintainenace above this is done by the decorator. The caching
    store itselfs decides how large to grow the cache and which data to keep,
    which data to throw away.

    :param cache: The caching backend.
    :param store: The backing store. This is the "authorative" backend.
    """
    def __init__(self, cache, store):
        super(CacheDecorator, self).__init__(store)
        self.cache = cache

    def delete(self, key):
        """Implementation of :meth:`~simplekv.KeyValueStore.delete`.

        If an exception occurs in either the cache or backing store, all are
        passing on.
        """
        self._dstore.delete(key)
        self.cache.delete(key)

    def get(self, key):
        """Implementation of :meth:`~simplekv.KeyValueStore.get`.

        If a cache miss occurs, the value is retrieved, stored in the cache and
        returned.

        If the cache raises an :exc:`~exceptions.IOError`, the cache is
        ignored, and the backing store is consulted directly.

        It is possible for a caching error to occur while attempting to store
        the value in the cache. It will not be handled as well.
        """
        try:
            return self.cache.get(key)
        except KeyError:
            # cache miss or error, retrieve from backend
            data = self._dstore.get(key)

            # store in cache and return
            self.cache.put(key, data)
            return data
        except IOError:
            # cache error, ignore completely and return from backend
            return self._dstore.get(key)

    def get_file(self, key, file):
        """Implementation of :meth:`~simplekv.KeyValueStore.get_file`.

        If a cache miss occurs, the value is retrieved, stored in the cache and
        returned.

        If the cache raises an :exc:`~exceptions.IOError`, the retrieval cannot
        proceed: If ``file`` was an open file, data maybe been written to it
        already. The :exc:`~exceptions.IOError` bubbles up.

        It is possible for a caching error to occur while attempting to store
        the value in the cache. It will not be handled as well.
        """
        try:
            return self.cache.get_file(key, file)
        except KeyError:
            # cache miss, load into cache
            fp = self._dstore.open(key)
            self.cache.put_file(key, fp)

            # return from cache
            return self.cache.get_file(key, file)
        # if an IOError occured, file pointer may be dirty - cannot proceed
        # safely

    def open(self, key):
        """Implementation of :meth:`~simplekv.KeyValueStore.open`.

        If a cache miss occurs, the value is retrieved, stored in the cache,
        then then another open is issued on the cache.

        If the cache raises an :exc:`~exceptions.IOError`, the cache is
        ignored, and the backing store is consulted directly.

        It is possible for a caching error to occur while attempting to store
        the value in the cache. It will not be handled as well.
        """
        try:
            return self.cache.open(key)
        except KeyError:
            # cache miss, load into cache
            fp = self._dstore.open(key)
            self.cache.put_file(key, fp)

            return self.cache.open(key)
        except IOError:
            # cache error, ignore completely and return from backend
            return self._dstore.open(key)

    def put(self, key, data):
        """Implementation of :meth:`~simplekv.KeyValueStore.put`.

        Will store the value in the backing store. After a successful or
        unsuccessful store, the cache will be invalidated by deleting the key
        from it.
        """
        try:
            return self._dstore.put(key, data)
        finally:
            self.cache.delete(key)

    def put_file(self, key, file):
        """Implementation of :meth:`~simplekv.KeyValueStore.put_file`.

        Will store the value in the backing store. After a successful or
        unsuccessful store, the cache will be invalidated by deleting the key
        from it.
        """
        try:
            return self._dstore.put_file(key, file)
        finally:
            self.cache.delete(key)
