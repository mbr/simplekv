#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import KeyValueStore
from .._compat import BytesIO

from .._compat import pickle
from bson.binary import Binary
import re


class MongoStore(KeyValueStore):
    """Uses a MongoDB collection as the backend, using pickle as a serializer.

    :param db: A (already authenticated) pymongo database.
    :param collection: A MongoDB collection name.
    """

    def __init__(self, db, collection):
        self.db = db
        self.collection = collection

    def _has_key(self, key):
        return self.db[self.collection].count_documents({"_id": key}) > 0

    def _delete(self, key):
        return self.db[self.collection].delete_one({"_id": key})

    def _get(self, key):
        try:
            item = next(self.db[self.collection].find({"_id": key}))
            return pickle.loads(item["v"])
        except StopIteration:
            raise KeyError(key)

    def _open(self, key):
        return BytesIO(self._get(key))

    def _put(self, key, value):
        self.db[self.collection].update_one(
            {"_id": key},
            {"$set": {"v": Binary(pickle.dumps(value))}},
            upsert=True)
        return key

    def _put_file(self, key, file):
        return self._put(key, file.read())

    def iter_keys(self, prefix=u""):
        for item in self.db[self.collection].find({"_id": {"$regex": '^' + re.escape(prefix)}}):
            yield item["_id"]
