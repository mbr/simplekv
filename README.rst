simple key-value storage api
============================

.. image:: https://travis-ci.org/mbr/simplekv.png?branch=master
   :target: https://travis-ci.org/mbr/simplekv

*simplekv* is an API for very basic key-value stores used for small, frequently
accessed data or large binary blobs. Its basic interface is easy to implement
and it supports a number of backends, including the filesystem, SQLAlchemy,
MongoDB, Redis and Amazon S3/Google Storage.

Installation
------------
simplekv is `available on PyPI <http://pypi.python.org/pypi/simplekv/>`_ and
can be installed through `pip <http://pypi.python.org/pypi/pip>`_::

   pip install simplekv

Documentation
-------------
The documentation for simplekv is available at
http://pythonhosted.org/simplekv.

License
-------
simplekv is `MIT licensed
<http://www.opensource.org/licenses/mit-license.php>`_.
