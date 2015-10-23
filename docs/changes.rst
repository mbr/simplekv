Changelog
*********

0.10.0
======
* simplekv no longer depends on ``six``.
* The :class:`~simplekv.decorator.PrefixDecorator` works more as expected.
* An experimental git-based store has been added in
  :class:`~simplekv.git.GitCommitStore`.


0.9.2
=====
* Added :class:`~simplekv.decorator.PrefixDecorator`.


0.9
===
* Deprecated the :class:`~simplekv.UrlKeyValueStore`, replaced by flexible
  mixins like :class:`~simplekv.UrlMixin`.
* Added :class:`~simplekv.TimeToLiveMixin` support (on
  :class:`~simplekv.memory.redisstore.RedisStore` and
  :class:`~simplekv.memory.memcachestore.MemcacheStore`).


0.6
===
* Now supports `redis <http://redis.io>`_ backend:
  :class:`~simplekv.memory.redisstore.RedisStore`.
* Fixed bug: No initial value for String() column in SQLAlchemy store.


0.5
===
* Maximum key length that needs to be supported by all backends is 250
  characters (was 256 before).
* Added `memcached <http://memcached.org>`_ backend:
  :class:`~simplekv.memory.memcachestore.MemcacheStore`
* Added `SQLAlchemy <http://sqlalchemy.org>`_ support:
  :class:`~simplekv.db.sql.SQLAlchemyStore`
* Added :mod:`simplekv.cache` module.


0.4
===
* Support for cloud-based storage using
  `boto <http://boto.cloudhackers.com/>`_ (see
  :class:`.BotoStore`).
* First time changes were recorded in docs


0.3
===
* **Major API Change**: Mixins replaced with decorators (see
  :class:`simplekv.idgen.HashDecorator` for an example)
* Added `simplekv.crypt`


0.1
===
* Initial release
