simple key-value storage api
============================

*simplekv* is an API for very basic key-value stores used for small, frequently
accessed data or large binary blobs. Its basic interface is easy to implement
and it supports a number of backends, including the filesystem, SQLAlchemy,
Redis and Amazon S3/Google Storage.

Installation
------------
simplekv is `available on PyPI <http://pypi.python.org/pypi/simplekv/>`_ and
can be installed through `pip <http://pypi.python.org/pypi/pip>`_ or
`easy_install <http://pypi.python.org/pypi/setuptools>`_:

::

   $ pip install simplekv


Development
-----------
`tox <https://pypi.python.org/pypi/tox>`_ is used to test packaging and python2.6 and python2.7 support.

::
   $ pip install tox
   $ tox


Documentation
-------------
The documentation for *simplekv* is available at
`<http://simplekv.readthedocs.org>`_.

License
-------
*simplekv* is `MIT licensed
<http://www.opensource.org/licenses/mit-license.php>`_.
