#!/usr/bin/env python
# coding=utf8

from itertools import imap

from boto.s3.key import Key
from boto.s3.bucket import Bucket
from boto.s3.connection import S3Connection
from boto.exception import BotoClientError, BotoServerError, S3ResponseError

from .. import UrlKeyValueStore


class S3Store(UrlKeyValueStore):
    def __init__(self, bucket, prefix='', url_valid_time=0):
        self.prefix = prefix.strip().lstrip('/')
        self.bucket = bucket
        self.url_valid_time = url_valid_time

    @classmethod
    def from_credentials(cls, access_key, secret_key,
                         bucket_name, *args, **kwargs):
        conn = S3Connection(access_key, secret_key)
        bucket = Bucket(conn, bucket_name)
        return S3Store(bucket, prefix='/')

    def iter_keys(self):
        try:
            prefix_len = len(self.prefix)
            return imap(lambda k: k.name[prefix_len:],
                        self.bucket.list(self.prefix))
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _has_key(self, key):
        try:
            return bool(self.bucket.get_key(self.prefix + key))
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _delete(self, key):
        try:
            self.bucket.delete_key(self.prefix + key)
        except S3ResponseError, e:
            if e.code != 'NoSuchKey':
                raise IOError(str(e))

    def _get(self, key):
        k = Key(self.bucket, self.prefix + key)
        try:
            return k.get_contents_as_string()
        except S3ResponseError, e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _get_file(self, key, file):
        k = Key(self.bucket, self.prefix + key)
        try:
            return k.get_contents_to_file(file)
        except S3ResponseError, e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _get_filename(self, key, filename):
        k = Key(self.bucket, self.prefix + key)
        try:
            return k.get_contents_to_filename(filename)
        except S3ResponseError, e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _open(self, key):
        k = Key(self.bucket, self.prefix + key)
        try:
            k.open_read()
            return k
        except S3ResponseError, e:
            if e.code == 'NoSuchKey':
                raise KeyError(key)
            raise IOError(str(e))
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _put(self, key, data):
        k = Key(self.bucket, self.prefix + key)
        try:
            k.set_contents_from_string(data)
            return key
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _put_file(self, key, file):
        k = Key(self.bucket, self.prefix + key)
        try:
            k.set_contents_from_file(file)
            return key
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _put_filename(self, key, filename):
        k = Key(self.bucket, self.prefix + key)
        try:
            k.set_contents_from_filename(filename)
            return key
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))

    def _url_for(self, key):
        k = Key(self.bucket, self.prefix + key)
        try:
            return k.generate_url(self.url_valid_time)
        except (BotoClientError, BotoServerError), e:
            raise IOError(str(e))
