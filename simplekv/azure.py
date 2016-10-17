#!/usr/bin/env python
# coding=utf8

import io

from azure.storage import CloudStorageAccount
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage._error import AzureException
from azure.storage._error import AzureHttpError

from . import KeyValueStore


class AzureBlockBlobStorage(KeyValueStore):
    def __init__(self, account, container, public=False, prefix=''):
        self.block_blob_service = account.create_block_blob_service()
        self.container = container
        self.public = public
        self.prefix = prefix

        self.block_blob_service.create_container(container, public_access=PublicAccess.Container if public else None)

    def __generate_key(self, key):
        return self.prefix + key

    def _delete(self, key):
        try:
            self.block_blob_service.delete_blob(self.container, self.__generate_key(key))
        except AzureHttpError as ex:
            raise IOError(str(ex))
        except AzureException as ex:
            raise KeyError(key)

    def _get(self, key):
        try:
            return self.block_blob_service.get_blob_to_text(self.container,  self.__generate_key(key)).content
        except AzureHttpError as ex:
            raise IOError(str(ex))
        except AzureException as ex:
            raise KeyError(key)

    def _has_key(self, key):
        try:
            return self.block_blob_service.exists(self.container,  self.__generate_key(key))
        except AzureHttpError as ex:
            raise IOError(str(ex))

    def iter_keys(self):
        try:
            return self.block_blob_service.list_blobs(self.container)
        except AzureHttpError as ex:
            raise IOError(str(ex))


    def _open(self, key):
        try:
            output_stream = io.BytesIO()
            self.block_blob_service.get_blob_to_stream(self.container,  self.__generate_key(key), output_stream)
            return output_stream
        except AzureHttpError as ex:
            raise IOError(str(ex))

    def _put(self, key, data):
        try:
            self.block_blob_service.create_blob_from_text(self.container,  self.__generate_key(key), data)
            return key
        except AzureHttpError as ex:
            raise IOError(str(ex))

    def _put_file(self, key, file):
        try:
            self.block_blob_service.create_blob_from_stream(self.container, self.__generate_key(key), file)
            return key
        except AzureHttpError as ex:
            raise IOError(str(ex))

    def _get_file(self, key, file):
        try:
            self.block_blob_service.get_blob_to_stream(self.container, self.__generate_key(key), file)
        except AzureHttpError as ex:
            raise IOError(str(ex))
        except AzureException as ex:
            raise KeyError(key) 

    def _get_filename(self, key, filename):
        try:
            self.block_blob_service.get_blob_to_path(self.container, self.__generate_key(key), filename)
        except AzureHttpError as ex:
            raise IOError(str(ex))
        except AzureException as ex:
            raise KeyError(key)

    def _put_filename(self, key, filename):
        try:
            self.block_blob_service.create_blob_from_path(self.container, self.__generate_key(key), filename)
            return key
        except AzureHttpError as ex:
            raise IOError(str(ex))