In-memory stores
****************
The simplest conceivable key-value store is found in
:class:`simplekv.memory.DictStore`.  It lends itself well for testing or
playing around with *simplekv*.

.. autoclass:: simplekv.memory.DictStore
   :members:

redis-backend
=============
The redis_-backend requires :py:mod:`redis` to be installed and uses a
redis_-database as a backend.

Currently, simplekv targets the latest stable redis version, but since it uses
very few commands available, it should work on older stables as well. Note that
some features are unsupported on older redis_-versions (such as sub-second
accuracy for TTL values on redis_ < 2.6) and will cause redis to complain.

.. autoclass:: simplekv.memory.redisstore.RedisStore

memcached-backend
=================
The memcached_-backend is not fully
:class:`~simplekv.KeyValueStore`-compliant, because some operations are not
supported on memcached. An :exc:`~exceptions.IOError` will be raised if that is
the case.

Due to the nature of memcache, attempting to store objects that are close to 1
megabyte in size or larger will most likely result in an
:exc:`~exceptions.IOError`, unless you increased memcached_'s limit at compile
time. This store also does not make any guarantees about persistancy, it is as
volatile as memcache itself and best used for caching.

.. class:: simplekv.memory.memcachestore.MemcacheStore

   A backend that uses python-memcached_ or pylibmc_ to connect to a
   memcached_ instance.

   Note that :meth:`~simplekv.KeyValueStore.__contains__` is not supported when
   using python-memcached_, while it usually works with pylibmc_.

   In addition to that, iterating the keys (using
   :meth:`~simplekv.KeyValueStore.__iter__`,
   :meth:`~simplekv.KeyValueStore.iter_keys`) and listing keys through
   :meth:`~simplekv.KeyValueStore.keys` is not supported at all [1]_.

   .. method:: __init__(mc)

      :param mc: A :class:`~pylibmc.Client` instance of python-memcached_ or
                 pylibmc_.

.. _python-memcached: http://pypi.python.org/pypi/python-memcached
.. _pylibmc: http://sendapatch.se/projects/pylibmc/
.. _memcached: http://memcached.org
.. _redis: http://redis.io
.. [1] The memcached_ protocol does not support listing/iterating over keys.
