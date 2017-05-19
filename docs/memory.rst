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
.. _redis: http://redis.io
