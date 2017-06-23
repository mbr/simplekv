#!/usr/bin/env python
# coding=utf8

from cStringIO import StringIO

from google.appengine.ext import ndb

from . import KeyValueStore


class NdbStore(KeyValueStore):
    def __init__(self, obj_class):
        self.obj_class = obj_class

    def _delete(self, key):
        db_key = ndb.Key(self.obj_class, key)
        db_key.delete()

    def _get(self, key):
        obj = self.obj_class.get_by_id(id=key)

        if not obj:
            raise KeyError(key)

        return obj.v

    def _has_key(self, key):
        return None != self.obj_class.get_by_id(id=key)

    def iter_keys(self, prefix=u""):
        qry_iter = self.obj_class.query().iter(keys_only=True)
        return filter(lambda k: k.string_id().startswith(prefix), (k.string_id() for k in qry_iter))

    def _open(self, key):
        return StringIO(self._get(key))

    def _put(self, key, data):
        obj = self.obj_class(id=key, v=data)
        obj.put()

        return obj.key.string_id()

    def _put_file(self, key, file):
        return self._put(key, file.read())
