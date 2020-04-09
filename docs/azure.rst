Microsoft Azure Blob Storage
****************************

Simplekv supports storing data in `Microsoft Azure Block Blob Storage <https://azure.microsoft.com/en-us/services/storage/blobs/>`_.

The backend uses the `azure-storage-blob <https://github.com/Azure/azure-storage-python/tree/master/azure-storage-blob>`_
python distribution to access the azure blob storage and currently supports versions 2.x and 12.x.

Note that ``azure-storage-blob`` is not a dependency for simplekv. You need to install it
manually, otherwise you will see an :exc:`~exceptions.ImportError`.

Here is a short example:

::

   from simplekv.net.azurestore import AzureBlockBlobStore

   conn_string = 'DefaultEndpointsProtocol=https;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;'

   store = AzureBlockBlobStore(conn_string=conn_string, container='MyContainerName', public=False)

   # at this point, we can use the store like any other
   store.put(u'some-key', b'Hello, World!')

   # print out what's behind some-key. you should be able to see it
   # in the container now as well
   print store.get(u'some-key')


Testing
=======

The tests for the azure backend either

 * use a real azure blob store account or
 * use the `Azurite <https://github.com/Azure/Azurite>`_ blob storage emulator

The travis tests use the second method.

To test with a real blob store account, edit the file ``azure_credentials.ini``
s.t. the first config section contains the actual account_name and account_key
of your test account.

To test against a locally running azurite instance make sure to start azurite::

 docker run -p 10000:10000 mcr.microsoft.com/azure-storage/azurite azurite-blob --blobHost 0.0.0.0 &

before running the tests.

To skip the tests of the azure backend, comment out the ``account_name`` in the ``azure_credentials.ini`` file.

.. autoclass:: simplekv.net.azurestore.AzureBlockBlobStore
