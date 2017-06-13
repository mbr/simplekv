kv-caches
*********

Caches speed up access to stores greatly, if used right. Usually, these require
combining two :class:`~simplekv.KeyValueStore` instances of the same or different
kind. A simple example without error-handling is a store that uses a
:class:`~simplekv.memory.redisstore.RedisStore` in front of a
:class:`~simplekv.fs.FilesystemStore`:

::

  from simplekv.memory.redisstore import RedisStore
  from simplekv.fs import FilesystemStore
  from simplekv.cache import CacheDecorator

  from redis import StrictRedis

  # initialize redis instance
  r = StrictRedis()

  store = CacheDecorator(
    cache=RedisStore(r),
    store=FilesystemStore('.')
  )

  # will store the value in the FilesystemStore
  store.put(u'some_value', '123')

  # fetches from the FilesystemStore, but caches the result
  print store.get(u'some_value')

  # any further calls to store.get('some_value') will be served from the
  # RedisStore now

.. automodule:: simplekv.cache
   :members:
