Transforms
**********

The class :mod:`simplekv.transform.ValueTransformingDecorator` decorates
a :class:`simplekv.KeyValueStore` and applies one or several transformation(s)
on the value before writing it to the decorated store.

Example to gzip everything before writing to an existing ``decorated_store`` ::

   from simplekv.transform import Gzip, ValueTransformingDecorator

   store = ValueTransformingDecorator(decorated_store, Gzip())
   store.put(u'key', b'value')

   # accessing via the decorator retrieves the original value:
   assert store.get(u'key') == b'value'

   # accessing decorated_store directly will retrieve the gip'ed value:
   from gzip import GzipFile

   assert GzipFile(fileobj=decorated_store.open(u'key'), mode='r').read() == b'value'

.. autoclass:: simplekv.transform.Gzip
.. autoclass:: simplekv.transform.Encrypt
    :members: generate_encryption_key
.. autoclass:: simplekv.transform.B64Encode
.. autoclass:: simplekv.transform.ValueTransformingDecorator
