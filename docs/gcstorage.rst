Google Cloud Storage
****************************

This backend is for storing data in `Google Cloud Storage <https://cloud.google.com/storage>`_
by using the ``google-cloud-storage`` library.

``google-cloud-storage`` is only available for Python 3. Simplekv also provides access to
Google Cloud Storage through :class:`~simplekv.net.boto.BotoStore` using the ``boto`` library which is available for Python 2.


Note that ``google-cloud-storage`` is not a dependency for simplekv. You need to install it
manually, otherwise you will see an :exc:`~exceptions.ImportError`.

Here is a short example:

::

   from simplekv.net.gcstore import GoogleCloudStore

   credentials_path = "/path/to/credentials.json"

   store = GoogleCloudStore(credentials=credentials_path, bucket_name="test_bucket")

   # store some data in the store
   store.put("first-key", b"Hello Google Cloud!")

   # print out what's behind first-key. You should now see
   # the key in the bucket as well
   print store.get("first-key")


Testing
=======

The tests for the google cloud storage backend either

 * use a real google cloud storage account
 * use the `Fake GCS Server <https://github.com/fsouza/fake-gcs-server>`_ storage emulator

The travis tests use the second method. Caution: Some methods (deleting buckets, copying blobs, ...) aren't implemented
in the emulator and should therefore be tested using a real cloud storage account.

To test with a real blob store account, edit the file ``google_cloud_credentials.ini``
s.t. the first config section contains the path to the ``credentials.json`` of your test account.

To test against a locally running Fake GCS Server instance make sure to start the docker container::

 docker run -d --name fake-gcs-server -p 4443:4443 fsouza/fake-gcs-server -scheme http

before running the tests.

.. autoclass:: simplekv.net.gcstore.GoogleCloudStore
    :members: __init__
