# coding=utf8

from .adapter import ReadAdapter, WriteAdapter
from .transformer import PipeTransformerPair
from ..decorator import StoreDecorator


class ValueTransformingDecorator(StoreDecorator):
    """Apply transformations on values before passing them to a ``decorated_store``

    :param store: the :class:`simplekv.KeyValueStore` to decorate
    :param transformations: the transformation or list/tuple of
      transformations to apply to the values. In case a list is given,
      they are applied from left-to-right before writing values to ``store``
      (and the inverse transformations from right-to-left after reading
      from ``store``).
    """

    def __init__(self, store, transformations):
        super(ValueTransformingDecorator, self).__init__(store)
        if isinstance(transformations, (list, tuple)):
            self._transformer_pair = PipeTransformerPair(transformations)
        else:
            self._transformer_pair = transformations

    def put(self, key, data, *args, **kwargs):
        transformer = self._transformer_pair.transformer()
        transformed = transformer.transform(data) + transformer.finalize()
        return self._dstore.put(key, transformed, *args, **kwargs)

    def get(self, key, *args, **kwargs):
        transformed = self._dstore.get(key, *args, **kwargs)
        transformer = self._transformer_pair.inverse()
        plain = transformer.transform(transformed) + transformer.finalize()
        return plain

    def put_file(self, key, file, *args, **kwargs):
        if isinstance(file, str):
            with open(file, 'rb') as f:
                return self.put_file(key, f, *args, **kwargs)
        adapter = ReadAdapter(file, self._transformer_pair.transformer())
        return self._dstore.put_file(key, adapter, *args, **kwargs)

    def get_file(self, key, file, *args, **kwargs):
        if isinstance(file, str):
            with open(file, 'wb') as f:
                return self.get_file(key, f, *args, **kwargs)
        adapter = WriteAdapter(file, self._transformer_pair.inverse())
        rv = self._dstore.get_file(key, adapter, *args, **kwargs)
        adapter.close()
        return rv

    def open(self, key, *args, **kwargs):
        file = self._dstore.open(key, *args, **kwargs)
        adapter = ReadAdapter(file, self._transformer_pair.inverse())
        return adapter

    def __getattr__(self, item):
        # only forward methods that operate merely on keys to the
        # underlying store.
        # So this deliberately does not forward all methods, such
        # as from the url mixin, as this would break invariants
        # (for example, users of the url mixing can reasonably expect that
        # downloading the data from the generated url matched what they
        # retrieve via the store's `get`).
        # Note that in particular, 'copy' is not exposed, as one should
        # always re-encrypt with a different nonce instead (i.e. implementing
        # copy via 'get' and 'put' will do that).
        if item in {'iter_keys', 'keys', 'delete'}:
            return getattr(self._dstore, item)
        raise AttributeError

    def __str__(self):
        return 'ValueTrafo({}, {})'.format(self._dstore,
                                           self._transformer_pair)
