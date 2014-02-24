#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import KeyValueStore, StringIO

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads
from bson.binary import Binary


class MongoStore(KeyValueStore):
    """Uses a MongoDB collection as the backend, using pickle as a serializer.

:param db: A (already authenticated) pymongo database.
:param collection: A MongoDB collection name, defaults to "sessions".
"""

    def __init__(self, db, collection):
        self.db = db
        self.collection = collection

    def _has_key(self, key):
        return self.db[self.collection].find({"_id": key}).count() > 0

    def _delete(self, key):
        return self.db[self.collection].remove({"_id": key})

    def _get(self, key):
        try:
            item = self.db[self.collection].find({"_id": key}).next()
            return loads(item["v"])
        except StopIteration:
            raise KeyError(key)

    def _open(self, key):
        return StringIO(self._get(key))

    def _put(self, key, value):
        self.db[self.collection].update({"_id": key},
                                        {"$set": {"v": Binary(dumps(value))}},
                                        upsert=True)
        return key

    def _put_file(self, key, file):
        return self._put(key, file.read())

    def iter_keys(self):
        for item in self.db[self.collection].find():
            yield item["_id"]
