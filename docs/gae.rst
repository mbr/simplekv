Google app engine support
*************************

Currently, there is support for storing data on `Google app engine
<https://developers.google.com/appengine/>`_ using ndb. This is mainly intended
for storing small bits of data, like sessions or similiar but not large binary
blobs [1]_.

.. class:: simplekv.gae.NdbStore

   A backend that stores data on ndb objects. The objects key will be the key
   in the kvstore, while an attribute ``v`` must be present on the object to
   store the data.

   .. method:: __init__(obj_class):

      :param obj_class: An instance of a `Model <https://developers.google.com/
                        appengine/docs/python/ndb/modelclass>`_ object.

Here is a minimal example:

::

    from google.appengine.ext import ndb
    from simplekv.gae import NdbStore

    class MyKvModel(ndb.Model):
        v = ndb.BlobProperty(indexed=False)

    store = NdbStore(MyKvModel)


.. [1] You're welcome to implement it and `submit a patch
   <https://github.com/mbr/simplekv>`_.
