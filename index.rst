simple key-value storage api
****************************

*simplekv* is an API for very basic key-value stores for storing binary data.
Due to its basic interface, it is easy to implemented a large number of
backends. *simplekv*'s origins are in storing user-uploaded files on websites,
but its low overhead and design should make it applicable for numerous other
problems.

Built upon the simple foundation are a few optional bells and whistles, such as
automatic ID generation/hashing (in :mod:`simplekv.idgen`).

Table of contents
-----------------

.. toctree::
   :maxdepth: 3

   filesystem
   memory
   idgen
   crypt

   changes

Why it's not a trendy NoSQL database
------------------------------------

There are many projects that offer a similiar functionality, so called "NoSQL"
databases like CouchDB_. *simplekv* is different in its goals:

no server dependencies
  *simplekv* does only depend on python and possibly a few libraries easily
  fetchable from PyPI_. You do not have to run and install any server software
  to use *simplekv*.

much, much simpler
  The database applications offer a whole lot more features than *simplekv*.
  This is by choice. Keep your metadata in a regular database, *simplekv* does
  only one thing for you: Store and retrieve binary data.

specializes in blobs
  The fastest, most basic *simplekv* backend implementation stores files on
  your harddrive and is just as fast. This underlines the focus on storing
  big blobs without overhead or metadata. A typical usecase is starting out
  small with local files and then migrating all your binary data to something
  like Amazon's S3_.

Should you require the simple feature-set of *simplekv*, but some of the
replication/scaling capabilities of a full "NoSQL" database, it should be easy
to use it as a backend for *simplekv* instead.

.. _CouchDB: http://couchdb.apache.org/
.. _PyPI: http://pypi.python.org
.. _S3: https://s3.amazonaws.com/

The core API
============

.. autoclass:: simplekv.KeyValueStore
   :members: __contains__, __iter__, delete, get, get_file, iter_keys, keys,
             open, put, put_file

In addition to that, an extended base class is available that provides an extra
method to support URL generation:

.. autoclass:: simplekv.UrlKeyValueStore
   :members: url_for

Implementing a new backend
--------------------------

Subclassing :class:`simplekv.KeyValueStore` is the fastest way to implement a
new backend. It suffices to override the
:func:`simplekv.KeyValueStore._delete`,
:func:`simplekv.KeyValueStore.iter_keys`,
:func:`simplekv.KeyValueStore._open` and
:func:`simplekv.KeyValueStore._put_file` methods, as all the other methods
have default implementations that call these.

After that, you can override any number of underscore-prefixed methods with
more specialized implementations to gain speed improvements.

Atomicity
---------
Every call to a method on a KeyValueStore results in a single operation on the
underlying backend. No guarantees are made above that, if you check if a key
exists and then try to retrieve it, it may have already been deleted in between
(instead, retrieve and catch the exception).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

