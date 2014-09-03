#!/usr/bin/env python
# coding=utf8

from itertools import imap

from boto.exception import BotoClientError, BotoServerError,\
                           StorageResponseError
from boto.s3.key import Key

from .. import KeyValueStore, UrlMixin


class BotoStore(KeyValueStore, UrlMixin):
    def __init__(self, bucket, prefix='', url_valid_time=0,
                 reduced_redundancy=False, public=False, metadata=None):
        self.prefix = prefix.strip().lstrip('/')
        self.bucket = bucket
        self.reduced_redundancy = reduced_redundancy
        self.public = public
        self.url_valid_time = url_valid_time
        self.metadata = metadata or {}

    def __new_key(self, name):
        k = Key(self.bucket, self.prefix + name)
        if self.metadata:
            k.update_metadata(self.metadata)
        return k

    def __upload_args(self):
        """Generates a dictionary of arguments to pass to various
        set_content_from* functions. This allows us to save API calls by
        passing the necessary parameters on with the upload."""
        d = {
            'reduced_redundancy': self.reduced_redundancy,
        }

        if self.public:
            d['policy'] = 'public-read'

        return d

    def iter_keys(self):
        try:
            prefix_len = len(self.prefix)
            return imap(lambda k: k.name[prefix_len:],
                        self.bucket.list(self.prefix))
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _has_key(self, key):
        try:
            return bool(self.bucket.get_key(self.prefix + key))
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _delete(self, key):
        try:
            self.bucket.delete_key(self.prefix + key)
        except StorageResponseError as e:
            if e.code != 'NoSuchKey':
                raise IOError(str(e))

    def _get(self, key):
        k = self.__new_key(key)
        try:
            return k.get_contents_as_string()
        except StorageResponseError as e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _get_file(self, key, file):
        k = self.__new_key(key)
        try:
            return k.get_contents_to_file(file)
        except StorageResponseError as e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _get_filename(self, key, filename):
        k = self.__new_key(key)
        try:
            return k.get_contents_to_filename(filename)
        except StorageResponseError as e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _open(self, key):
        k = self.__new_key(key)
        try:
            k.open_read()
            return k
        except StorageResponseError as e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _put(self, key, data):
        k = self.__new_key(key)
        try:
            k.set_contents_from_string(
                data, **self.__upload_args()
            )
            return key
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _put_file(self, key, file):
        k = self.__new_key(key)
        try:
            k.set_contents_from_file(
                file, **self.__upload_args()
            )
            return key
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _put_filename(self, key, filename):
        k = self.__new_key(key)
        try:
            k.set_contents_from_filename(
                filename, **self.__upload_args()
            )
            return key
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))

    def _url_for(self, key):
        k = self.__new_key(key)
        try:
            return k.generate_url(expires_in=self.url_valid_time,
                                  query_auth=False)
        except (BotoClientError, BotoServerError) as e:
            raise IOError(str(e))
