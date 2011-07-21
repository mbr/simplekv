Changelog
*********

0.5
===
* Maximum key length that needs to be supported by all backends is 250
  characters (was 256 before).
* Added `memcached <http://memcached.org>`_ backend:
  :class:`~simplekv.memory.memcachestore.MemcacheStore`
* Added `SQLAlchemy <http://sqlalchemy.org>`_ support:
  :class:`~simplekv.db.sql.SQLAlchemyStore`

0.4
===
* Support for cloud-based storage using
  `boto <http://boto.cloudhackers.com/>`_ (see
  :class:`simplekv.net.botostore.BotoStore`).
* First time changes were recorded in docs

0.3
===
* **Major API Change**: Mixins replaced with decorators (see
  :class:`simplekv.idgen.HashDecorator` for an example)
* Added `simplekv.crypt`

0.1
===
* Initial release
