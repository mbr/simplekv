kv-caches
*********

Caches speed up access to stores greatly, if used right. Usually, these require
combining two :class:`~simplekv.KeyValueStore` instances of the same or different
kind. A typical example is a store that uses a
:class:`~simplekv.memory.memcachestore.MemcacheStore` in front of a
:class:`~simplekv.fs.FilesystemStore`:

::

  from simplekv.memory.memcachestore import MemcacheStore
  from simplekv.fs import FilesystemStore
  from simplekv.cache import CacheDecorator

  import memcache

  # initialize memcache instance
  mc = memcache.Client(['localhost:11211'])

  store = CacheDecorator(
    cache=MemcacheStore(mc),
    store=FilesystemStore('.')
  )

  # will store the value in the FilesystemStore
  store.put('some_value', '123')

  # fetches from the FilesystemStore, but caches the result
  print store.get('some_value')

  # any further calls to store.get('some_value') will be served from the
  # MemcacheStore now

.. automodule:: simplekv.cache
   :members:
