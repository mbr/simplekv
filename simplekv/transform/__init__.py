# coding=utf-8
"""
Value-transforming decorators.

To construct a KeyValueStore that first gzips the data and then encodes
it using base64, use::

    dstore = DictStore()  # or any other store
    store = ValueTransformingDecorator(dstore, [Gzip(), B64Encode()])
    store.put(key, value)

The list of transformations will be applied from left to right
to the data passed to store, and the transformed data is forwarded
to the decorated store. So in the example
above, `dstore` will contain the value::

   base64.b64encode(gzip.compress(value))


"""
from .decorator import ValueTransformingDecorator
from .gzip import Gzip
from .b64encode import B64Encode

__all__ = ['ValueTransformingDecorator', 'Gzip', 'B64Encode']

try:
    from .encrypt import Encrypt  # noqa:F401
    __all__.append('Encrypt')
except ImportError:
    pass
