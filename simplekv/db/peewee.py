# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from io import BytesIO

from .._compat import imap
from .. import KeyValueStore

from peewee import Model, BlobField, CharField


class PeeweeStore(KeyValueStore):

    def __init__(self, db, tablename='key_value_store'):
        self._db = db
        self._model = self._create_model_class(db, tablename)

    @property
    def model(self):
        if not self._model.table_exists():
            self._db.create_table(self._model)
        return self._model

    def _create_model_class(self, db, tablename):
        class KeyValue(Model):
            key = CharField(
                index=True,
                primary_key=True,
                max_length=250
            )
            value = BlobField(null=True)

            class Meta:
                database = db
                db_table = tablename
        return KeyValue

    def _has_key(self, key):
        return self.model.select().where(
            self.model.key == key
        ).exists()

    def _get_obj(self, key):
        try:
            return self.model.get(key=key)
        except self.model.DoesNotExist:
            raise KeyError(key)

    def _delete(self, key):
        obj = self._get_obj(key)
        obj.delete_instance()

    def _get(self, key):
        return self._get_obj(key).value

    def _open(self, key):
        return BytesIO(self._get(key))

    def _put(self, key, data):
        obj = self.model.get_or_create(key=key)
        obj.value = data
        obj.save()
        return obj.key

    def _put_file(self, key, file):
        return self._put(key, file.read())

    def iter_keys(self):
        return imap(lambda v: v.key,
                    self.model.select(self.model.key))
