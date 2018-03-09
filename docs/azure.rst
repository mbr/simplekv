Microsoft Azure Blob Storage
****************************

Simplekv supports storing data in `Microsoft Azure Block Blob Storage <https://azure.microsoft.com/en-us/services/storage/blobs/>`_.

The backend uses the `azure-storage-blob <https://github.com/Azure/azure-storage-python/tree/master/azure-storage-blob>`_
python distribution to access the azure blob storage. Note that `azure-storage-blob` is not
a dependency for simplekv. You need to install it manually, otherwise you will see an :exc:`~exceptions.ImportError`.

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


Unit testing
============

The unit-tests for the azure backend are either run by travis on the main repo, or if you provide
your own credentials via a `azure_credentials.ini`` file in the root folder of the project.
An example looks like this:

::

  [my-azure-test-account]
  account_name=my_account_name
  account_key=AZURE_TEST_KEY

.. autoclass:: simplekv.net.azurestore.AzureBlockBlobStore
