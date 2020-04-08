Changelog
*********

0.14.1
======

* Fix support for ``key in store`` for azure with ``azure-storage-blob`` 12

0.14.0
======

* Add support for ``azure-storage-blob`` version 12. (``azure-storage-blob`` version 2 is still supported.)

0.13.1
======

* Add the optional parameters of the Azure API max_block_size and max_single_put_size to the AzureBlockBlobStore.

0.13.0
======
* Add ``iter_prefixes()`` method to iterate over all prefixes currently in the store, in any order. The
        prefixes are listed up to the given delimiter.

0.12.0
======

* Use ``BlockBlobService.list_blob_names`` in :meth:`simplekv.net.azurestore.AzureBlockBlobStore.iter_keys``.
  This will only parse the names from Azure's XML response thus reducing CPU time
  siginificantly for this function.
* They ``.keys()`` method on Python 3 now returns a list. This is in line with the documentation and the
  behaviour on Python 2. It used to return a generator.

0.11.11
====

* Fix file-descriptor leak in `KeyValueStore._get_file`

0.11.10
=======

* Azure files handles now correctly implement seek and return the new position.

0.11.9
======
* Add option to set the checksum for Azure blobs.
* Make the FilesystemStore resilient to parallel directory creations.

0.11.8
======
* Depend on azure-storage-blob, following the new naming scheme.
* Pass the max_connections parameter to Azure backend.

0.11.7
======
* removed seek() and tell() API for file handles opened in the botostore, due to it leaking HTTP connections to S3.

0.11.6
======
* Support seek() and tell() API for file handles opened in the botostore.

0.11.5
======
* Fix one off in open() method interfaces for azure backend

0.11.4
======
* The open() method in the azure backend now supports partial reads of blobs
* The exceptions from the azure backend contain more human-readable information in case of common errors.

0.11.3
======
* Apply 0.11.2 in ExtendedKeySpaceMixin as well

0.11.2
======
* Restore old behaviour of accepting valid keys of type `str` on Python 2

0.11.1
======
* Fix version in setup.py

0.11.0
======
* The memcached backend has been removed
* Keys have to be provided as unicode strings
* Values have to be provided as bytes (python 2) or as str (python 3)
* keys() and iter_keys() provide a parameter to iterate just over all keys with a given prefix
* Added :class:`simplekv.CopyMixin` to allow access to copy operations to
  backends which support a native copy operation
* Added a decorator which provides a read-only view of a store:
  :class:`~simplekv.decorator.ReadOnlyDecorator`
* Added a decorator which url-encodes all keys:
  :class:`~simplekv.decorator.URLEncodeKeysDecorator`
* Added a Microsoft Azure Blob Storage backend:
  :class:`~simplekv.net.azurestore.AzureBlockBlobStore`
* Added :class:`~simplekv.contrib.ExtendedKeyspaceMixin` which allows slashes and spaces in key names
  This mixin is experimental, unsupported and might not work with all backends.


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
  simplekv.memory.memcachestore.MemcacheStore).


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
  simplekv.memory.memcachestore.MemcacheStore
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
