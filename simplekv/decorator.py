#!/usr/bin/env python
# coding=utf8


class StoreDecorator(object):
    """Base class for store decorators.

    The default implementation will use :func:`getattr` to pass through all
    attribute/method requests to an underlying object stored as
    :attr:`_dstore`. It will also pass through the :attr:`__getattr__` and
    :attr:`__contains__` python special methods.
    """

    def __init__(self, store):
        self._dstore = store

    def __getattr__(self, attr):
        return getattr(self._dstore, attr)

    def __contains__(self, *args, **kwargs):
        return self._dstore.__contains__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._dstore.__iter__(*args, **kwargs)


class KeyTransformingDecorator(StoreDecorator):
    # currently undocumented (== not advertised as a feature)
    def _map_key(self, key):
        return key

    def _unmap_key(self, key):
        return key

    def _filter(self, key):
        return True

    def __contains__(self, key):
        return self._map_key(key) in self._dstore

    def __iter__(self):
        return self.iter_keys()

    def delete(self, key):
        return self._dstore.delete(self._map_key(key))

    def get(self, key, *args, **kwargs):
        return self._dstore.get(self._map_key(key), *args, **kwargs)

    def get_file(self, key, *args, **kwargs):
        return self._dstore.get_file(self._map_key(key), *args, **kwargs)

    def iter_keys(self):
        return (self._unmap_key(k) for k in self._dstore.iter_keys()
                if self._filter(k))

    def keys(self):
        """Return a list of keys currently in store, in any order

        :raises IOError: If there was an error accessing the store.
        """
        return list(self.iter_keys())

    def open(self, key):
        return self._dstore.open(self._map_key(key))

    def put(self, key, *args, **kwargs):
        return self._unmap_key(
            self._dstore.put(self._map_key(key), *args, **kwargs))

    def put_file(self, key, *args, **kwargs):
        return self._unmap_key(
            self._dstore.put_file(self._map_key(key), *args, **kwargs))

    # support for UrlMixin
    def url_for(self, key, *args, **kwargs):
        return self._dstore.url_for(self._map_key(key), *args, **kwargs)


class PrefixDecorator(KeyTransformingDecorator):
    """Prefixes any key with a string before passing it on the decorated
    store. Automatically strips the prefix upon key retrieval.

    :param store: The store to pass keys on to.
    :param prefix: Prefix to add.
    """

    def __init__(self, prefix, store):
        super(PrefixDecorator, self).__init__(store)
        self.prefix = prefix

    def _filter(self, key):
        return key.startswith(self.prefix)

    def _map_key(self, key):
        self._check_valid_key(key)
        return self.prefix + key

    def _unmap_key(self, key):
        assert key.startswith(self.prefix)

        return key[len(self.prefix):]
