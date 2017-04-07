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

    def _map_key_prefix(self, key_prefix):
        return key_prefix

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

    def iter_keys(self, prefix=""):
        return (self._unmap_key(k) for k in self._dstore.iter_keys(self._map_key_prefix(prefix))
                if self._filter(k))

    def keys(self, prefix=""):
        """Return a list of keys currently in store, in any order

        :raises IOError: If there was an error accessing the store.
        """
        return list(self.iter_keys(prefix))

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

    # support for CopyRenameDecorator
    def _copy(self, source, dest):
        return self._dstore._copy(self._map_key(source), self._map_key(dest))

    def _rename(self, source, dest):
        return self._dstore._rename(self._map_key(source), self._map_key(dest))


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

    def _map_key_prefix(self, key_prefix):
        return self.prefix + key_prefix

    def _unmap_key(self, key):
        assert key.startswith(self.prefix)

        return key[len(self.prefix):]


class CopyRenameDecorator(StoreDecorator):
    """Exposes a copy and rename API. This API is either backed by corresponding backend operations, if available,
    or emulated using get/put/delete.
    
    Warning: This makes the operations potentially not atomic"""
    def copy(self, source, dest):
        """Copies a key. The destination is overwritten if does exist.

        In case there is no native backend method available to do so, uses get and put to emulate the copy.
        :param source: The source key to copy
        :param dest: The destination for the copy

        :returns The destination key

        :raises exceptions.ValueError: If the source or target key are not valid
        :raises exceptions.KeyError: If the source key was not found"""
        self._check_valid_key(source)
        self._check_valid_key(dest)
        return self._copy(source, dest)

    def rename(self, source, dest):
        """Renames a key. The destination is overwritten if does exist.

        In case there is no native backend method available to do so, uses copy and delete to emulate the rename.
        :param source: The source key to rename
        :param dest: The new name of the key

        :returns The destination key

        :raises exceptions.ValueError: If the source or dest key are not valid
        :raises exceptions.KeyError: If the source key was not found"""
        self._check_valid_key(source)
        self._check_valid_key(dest)
        return self._rename(source, dest)
