#!/usr/bin/env python
# coding=utf8
from ._compat import quote_plus, unquote_plus, text_type, binary_type


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

    def iter_keys(self, prefix=u""):
        return (self._unmap_key(k) for k in self._dstore.iter_keys(self._map_key_prefix(prefix))
                if self._filter(k))

    def keys(self, prefix=u""):
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

    # support for CopyMixin
    def copy(self, source, dest):
        return self._dstore.copy(self._map_key(source), self._map_key(dest))


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


class URLEncodeKeysDecorator(KeyTransformingDecorator):
    """URL-encodes keys before passing them on to the underlying store."""
    def _map_key(self, key):
        if not isinstance(key, text_type):
            raise ValueError('%r is not a unicode string' % key)
        quoted = quote_plus(key.encode('utf-8'))
        if isinstance(quoted, binary_type):
            quoted = quoted.decode('utf-8')
        return quoted

    def _map_key_prefix(self, key_prefix):
        return self._map_key(key_prefix)

    def _unmap_key(self, key):
        return unquote_plus(key)


class ReadOnlyDecorator(StoreDecorator):
    """
    A read-only view of an underlying simplekv store

    Provides only access to the following methods/attributes of the
    underlying store: get, iter_keys, keys, open, get_file.
    It also forwards __contains__.
    Accessing any other method will raise AttributeError.

    Note that the original store for r/w can still be accessed,
    so using this class as a wrapper only provides protection
    against bugs and other kinds of unintentional writes;
    it is not meant to be a real security measure.
    """

    def __getattr__(self, attr):
        if attr in ('get', 'iter_keys', 'keys', 'open', 'get_file'):
            return super(ReadOnlyDecorator, self).__getattr__(attr)
        else:
            raise AttributeError
