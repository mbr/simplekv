simple key-value storage api
============================

*simplekv* is an API for very basic key-value stores for storing binary data.
Due to its basic interface, it is easy to implemented a large number of
backends. *simplekv*'s origins are in storing user-uploaded files on websites,
but its low overhead and design should make it applicable for numerous other
problems.

Features include storage in memory, local and remote filesystems and cloud
storage services such as `Amazon S3 <http://aws.amazon.com/s3/>`_ and `Google
Storage <http://code.google.com/apis/storage/>`_.

Installation
------------
simplekv is `available on PyPI <http://pypi.python.org/pypi/simplekv/>`_ and
can be installed through `pip <http://pypi.python.org/pypi/pip>`_ or
`easy_install <http://pypi.python.org/pypi/setuptools>`_:

::

   $ pip install simplekv

Documentation
-------------
The documentation for *simplekv* is available at
`<http://simplekv.readthedocs.org>`_.

License
-------
*simplekv* is `MIT licensed
<http://www.opensource.org/licenses/mit-license.php>`_.
