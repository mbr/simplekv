#!/usr/bin/env python
# coding=utf8

import io
from contextlib import contextmanager

from .._compat import binary_type, copyreg
from .. import KeyValueStore


def lazy_property(fn):
    """Decorator that makes a property lazy-evaluated."""
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property


@contextmanager
def map_azure_exceptions(key=None, exc_pass=()):
    """Map Azure-specific exceptions to the simplekv-API."""
    from azure.common import AzureMissingResourceHttpError, AzureHttpError,\
        AzureException
    try:
        yield
    except AzureMissingResourceHttpError as ex:
        if ex.__class__.__name__ not in exc_pass:
            raise KeyError(key)
    except AzureHttpError as ex:
        if ex.__class__.__name__ not in exc_pass:
            raise IOError(str(ex))
    except AzureException as ex:
        if ex.__class__.__name__ not in exc_pass:
            raise KeyError(key)


class AzureBlockBlobStore(KeyValueStore):
    def __init__(self, conn_string=None, container=None, public=False,
                 create_if_missing=True):
        self.conn_string = conn_string
        self.container = container
        self.public = public
        self.create_if_missing = create_if_missing

    # This allows recreating the block_blob_service instance when needed.
    # Together with the copyreg-registration at the bottom of this file,
    # allows the store object to be pickled and unpickled.
    @lazy_property
    def block_blob_service(self):
        from azure.storage.blob import BlockBlobService, PublicAccess
        block_blob_service = BlockBlobService(
            connection_string=self.conn_string)
        if self.create_if_missing:
            block_blob_service.create_container(
                self.container,
                public_access=PublicAccess.Container if self.public else None
            )
        return block_blob_service

    def _delete(self, key):
        with map_azure_exceptions(key=key,
                                  exc_pass=['AzureMissingResourceHttpError']):
            self.block_blob_service.delete_blob(self.container, key)

    def _get(self, key):
        with map_azure_exceptions(key=key):
            return self.block_blob_service.get_blob_to_bytes(
                self.container, key).content

    def _has_key(self, key):
        with map_azure_exceptions(key=key):
            return self.block_blob_service.exists(self.container, key)

    def iter_keys(self, prefix=u""):
        if prefix == "":
            prefix = None
        with map_azure_exceptions():
            blobs = self.block_blob_service.list_blobs(self.container, prefix=prefix)
            return (blob.name.decode('utf-8') if isinstance(blob.name, binary_type)
                    else blob.name for blob in blobs)

    def _open(self, key):
        with map_azure_exceptions(key=key):
            output_stream = io.BytesIO()
            self.block_blob_service.get_blob_to_stream(self.container, key,
                                                       output_stream)
            output_stream.seek(0)
            return output_stream

    def _put(self, key, data):
        with map_azure_exceptions(key=key):
            if isinstance(data, binary_type):
                self.block_blob_service.create_blob_from_bytes(self.container,
                                                               key, data)
            else:
                raise TypeError('Wrong type, expecting str or bytes.')
            return key

    def _put_file(self, key, file):
        with map_azure_exceptions(key=key):
            self.block_blob_service.create_blob_from_stream(self.container,
                                                            key, file)
            return key

    def _get_file(self, key, file):
        with map_azure_exceptions(key=key):
            self.block_blob_service.get_blob_to_stream(self.container, key,
                                                       file)

    def _get_filename(self, key, filename):
        with map_azure_exceptions(key=key):
            self.block_blob_service.get_blob_to_path(self.container, key,
                                                     filename)

    def _put_filename(self, key, filename):
        with map_azure_exceptions(key=key):
            self.block_blob_service.create_blob_from_path(self.container, key,
                                                          filename)
            return key


def pickle_azure_store(store):
    return store.__class__, (store.conn_string, store.container, store.public,
                             store.create_if_missing)

copyreg.pickle(AzureBlockBlobStore, pickle_azure_store)
