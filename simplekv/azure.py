#!/usr/bin/env python
# coding=utf8

from azure.storage import CloudStorageAccount
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage._error import AzureException
from azure.storage._error import AzureHttpException

import io

class AzureBlockBlobStorage(KeyValueStore):
    def __init__(self, block_blob_service, container, public=False, prefix=''):
        self.block_blob_service = block_blob_service
        self.container = container
        self.public = public
        self.prefix = prefix

        self.block_blob_service.create_container(container, public_access=PublicAccess.Container if public else None)

    def __generate_key(self, key)
        return self.prefix + key

    def _delete(self, key):
        try:
            self.block_blob_service.delete_blob(container, self.__generate_key(key))
        except AzureHttpError as ex:
            raise IOError(str(ex))
        except AzureException as ex:
            raise KeyError(key)

    def _get(self, key):
        try:
            return self.get_blob_to_text(container,  self.__generate_key(key)
        except AzureHttpError as ex:
            raise IOError(str(ex))
        except AzureException as ex:
            raise KeyError(key)

    def _has_key(self, key):
        try:
            return self.block_blob_service.exists(container,  self.__generate_key(key)
        raise AzureHttpException as ex:
            raise IOError(str(ex))

    def iter_keys(self):
        try:
            return self.block_blob_service.list_blobs(container)
        raise AzureHttpException as ex:
            raise IOError(str(ex))


    def _open(self, key):
        try:
            output_stream = io.BytesIO()
            self.block_blob_service.get_blob_to_stream(container,  self.__generate_key(key), output_stream)
            return output_stream
        raise AzureHttpException as ex:
            raise IOError(str(ex))

    def _put(self, key, data):
        try:
            self.block_blob_service.create_blob_from_text(container,  self.__generate_key(key), data)
            return key
        raise AzureHttpException as ex:
            raise IOError(str(ex))

    def _put_file(self, key, file):
        try:
            self.block_blob_service.create_blob_from_path(container,  self.__generate_key(key), file)
            return key
        raise AzureHttpException as ex:
            raise IOError(str(ex))