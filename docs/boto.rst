.. cannot use auto-doc here, we do not want boto as a dependency for building
   the docs!

Network and cloud-based storage
*******************************
A core feature of simplekv is the ability to transparently store data using
cloud storage services like `Amazon S3 <http://aws.amazon.com/s3/>`_ and `Google
Storage <http://code.google.com/apis/storage/>`_. This is achieved by providing
a backend that utilizes `boto <http://boto.cloudhackers.com/>`_ (preferably >=
2.25).

``boto`` doesn't support using Google Storage with Python3. For this
reason simplekv has a separate Google Storage implementation for Python3 at
:class:`~simplekv.net.gcstore.GoogleCloudStore` which uses Google's
``google-cloud-storage`` library.

Note that boto is not a dependency for simplekv. You need to install it
manually, otherwise you will see an :exc:`~exceptions.ImportError`.

Here is a short example:

::

   from simplekv.net.botostore import BotoStore
   import boto

   con = boto.connect_s3('your_access_key', 'your_secret_key')

   # use get_bucket instead, if you already have one!
   bucket = con.create_bucket('simplekv-testbucket')

   store = BotoStore(bucket)

   # at this point, we can use the store like any other
   store.put(u'some-key', b'Hello, World!')

   # print out what's behind some-key. you should be able to see it
   # in the bucket now as well
   print store.get(u'some-key')


Unit testing
============

The unit-tests for the boto storage can only run if you have access to a Google
Storage and/or Amazon S3 account. The tests will look in a file
``boto_credentials.ini`` in the simplekv source root folder for account
credentials, here is an example file:

::

  [s3]
  access_key = YOUR_AMAZON_S3_ACCESS_KEY
  secret_key = YOUR_AMAZON_S3_SECRET_KEY
  connect_func = connect_s3

  [gs]
  access_key = YOUR_GOOGLE_STORAGE_ACCESS_KEY
  secret_key = YOUR_GOOGLE_STORAGE_SECRET_KEY
  connect_func = connect_gs

If a section is not present, the tests for that backend will be skipped.

The unit tests for S3 will be run by travis against a local minio instance, emulating S3.


.. class:: simplekv.net.boto.BotoStore

   Backend using the storage api of boto.

   .. method:: __init__(bucket, prefix='', url_valid_time=0, reduced_redundancy=False, public=False, metadata=None)

      Constructs a new boto based backend.

      :param bucket: An instance of :class:`boto.s3.bucket.Bucket`,
                     :class:`boto.gs.bucket.Bucket` or similiar.
      :param prefix: A string that will transparently prefixed to all handled
                     keys.
      :param url_valid_time=0: When using
                     :meth:`~.UrlMixin.url_for`, URLs should be
                     valid for this many seconds at most.
      :param reduced_redundancy: Use reduced redundancy storage for
                                       storing keys.
      :param public: If set, all newly updated values will be made public
                     immediately.
      :param metadata: If set, for all newly created keys to be saved with
                       these metadata values.
