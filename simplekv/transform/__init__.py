"""
Value-transforming decorators.

To construct a SimpleKeyValueStore that first gzips the data and then encodes
it using base64, use::

    dstore = DictStore()  # or any other store
    store = apply_value_trafo(dstore, [gzip(), b64encode()])
    store.put(key, value)

The list of transformations will be applied from left to right
to the 'local' data (i.e. the data passed to `put`). So in the example
above, `dstore` will contain::

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
