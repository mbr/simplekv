simple key-value storage api
****************************

*simplekv* is an API for key-value store of binary data.  Due to its basic
interface, it is easy to implemented a large number of backends. *simplekv*'s
origins are in storing user-uploaded files on websites, but its low overhead
and design should make it applicable for numerous other problems, an example is
a `session backend for the Flask framework
<https://github.com/mbr/flask-kvsession>`_.

Built upon the solid foundation are a few optional bells and whistles, such as
automatic ID generation/hashing (in :mod:`simplekv.idgen`). A number of
backends are available, ranging from :class:`~simplekv.fs.FilesystemStore` to
support for `Amazon S3 <http://aws.amazon.com/s3/>`_ and `Google
Storage <http://code.google.com/apis/storage/>`_ through
:class:`~simplekv.net.botostore.BotoStore`.

Table of contents
=================
.. toctree::
   :maxdepth: 3

   filesystem
   net
   memory
   db
   idgen
   crypt
   cache

   changes

It's not a NoSQL database
------------------------------------
There are many projects that offer a similiar functionality, so called "NoSQL"
databases like CouchDB_. *simplekv* is different in its goals:

no server dependencies
  *simplekv* does only depend on python and possibly a few libraries easily
  fetchable from PyPI_, if you want to use extra features. You do not have to
  run and install any server software to use *simplekv*.

less features
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

.. autodata:: simplekv.VALID_KEY_REGEXP

.. autodata:: simplekv.VALID_KEY_RE

Implementing a new backend
==========================
Subclassing :class:`~simplekv.KeyValueStore` is the fastest way to implement a
new backend. It suffices to override the
:func:`~simplekv.KeyValueStore._delete`,
:func:`~simplekv.KeyValueStore.iter_keys`,
:func:`~simplekv.KeyValueStore._open` and
:func:`~simplekv.KeyValueStore._put_file` methods, as all the other methods
have default implementations that call these.

After that, you can override any number of underscore-prefixed methods with
more specialized implementations to gain speed improvements.

Default implementation
----------------------
Classes derived from :class:`~simplekv.KeyValueStore` inherit a number of
default implementations for the core API mehthods. Specifically, the
:func:`~simplekv.KeyValueStore.delete`,
:func:`~simplekv.KeyValueStore.get`,
:func:`~simplekv.KeyValueStore.get_file`,
:func:`~simplekv.KeyValueStore.keys`,
:func:`~simplekv.KeyValueStore.open`,
:func:`~simplekv.KeyValueStore.put`,
:func:`~simplekv.KeyValueStore.put_file`,
methods will each call the :func:`~simplekv.KeyValueStore._check_valid_key` method if a key has been provided and then call one of the following protected methods:

.. automethod:: simplekv.KeyValueStore._check_valid_key
.. automethod:: simplekv.KeyValueStore._delete
.. automethod:: simplekv.KeyValueStore._get
.. automethod:: simplekv.KeyValueStore._get_file
.. automethod:: simplekv.KeyValueStore._get_filename
.. automethod:: simplekv.KeyValueStore._has_key
.. automethod:: simplekv.KeyValueStore._open
.. automethod:: simplekv.KeyValueStore._put
.. automethod:: simplekv.KeyValueStore._put_file
.. automethod:: simplekv.KeyValueStore._put_filename

Atomicity
=========
Every call to a method on a KeyValueStore results in a single operation on the
underlying backend. No guarantees are made above that, if you check if a key
exists and then try to retrieve it, it may have already been deleted in between
(instead, retrieve and catch the exception).

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
