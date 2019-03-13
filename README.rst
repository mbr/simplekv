simple key-value storage api
============================

.. image:: https://travis-ci.org/mbr/simplekv.png?branch=master
   :target: https://travis-ci.org/mbr/simplekv
.. image:: https://coveralls.io/repos/github/mbr/simplekv/badge.svg?branch=master
   :target: https://coveralls.io/github/mbr/simplekv?branch=master

*simplekv* is an API for very basic key-value stores used for small, frequently
accessed data or large binary blobs. Its basic interface is easy to implement
and it supports a number of backends, including the filesystem, SQLAlchemy,
MongoDB, Redis and Amazon S3/Google Storage.

Installation
------------
simplekv is `available on PyPI <http://pypi.python.org/pypi/simplekv/>`_ and
can be installed through `pip <http://pypi.python.org/pypi/pip>`_::

   pip install simplekv
   
or via ``conda`` on `conda-forge <https://github.com/conda-forge/simplekv-feedstock>`_::

  conda install -c conda-forge simplekv

Documentation
-------------
The documentation for simplekv is available at
https://simplekv.readthedocs.io.

License
-------
simplekv is `MIT licensed
<http://www.opensource.org/licenses/mit-license.php>`_.
