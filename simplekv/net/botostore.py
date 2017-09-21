#!/usr/bin/env python
# coding=utf8

from .._compat import imap
from .. import KeyValueStore, UrlMixin, CopyMixin
from contextlib import contextmanager


@contextmanager
def map_boto_exceptions(key=None):
    """Map boto-specific exceptions to the simplekv-API."""
    from boto.exception import BotoClientError, BotoServerError, \
        StorageResponseError
    try:
        yield
    except (BotoClientError, BotoServerError, StorageResponseError) as e:
        if getattr(e, 'code', None) == 'NoSuchKey':
            raise KeyError(key)
        raise IOError(str(e))


class BotoStore(KeyValueStore, UrlMixin, CopyMixin):
    def __init__(self, bucket, prefix='', url_valid_time=0,
                 reduced_redundancy=False, public=False, metadata=None):
        self.prefix = prefix.strip().lstrip('/')
        self.bucket = bucket
        self.reduced_redundancy = reduced_redundancy
        self.public = public
        self.url_valid_time = url_valid_time
        self.metadata = metadata or {}

    def __new_key(self, name):
        from boto.s3.key import Key

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

    def iter_keys(self, prefix=u""):
        with map_boto_exceptions():
            prefix_len = len(self.prefix)
            return imap(lambda k: k.name[prefix_len:],
                        self.bucket.list(self.prefix + prefix))

    def _has_key(self, key):
        with map_boto_exceptions(key=key):
            return bool(self.bucket.get_key(self.prefix + key))

    def _delete(self, key):
        from boto.exception import StorageResponseError
        try:
            self.bucket.delete_key(self.prefix + key)
        except StorageResponseError as e:
            if e.code != 'NoSuchKey':
                raise IOError(str(e))

    def _get(self, key):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            return k.get_contents_as_string()

    def _get_file(self, key, file):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            return k.get_contents_to_file(file)

    def _get_filename(self, key, filename):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            return k.get_contents_to_filename(filename)

    def _open(self, key):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            k.open_read()
            return k

    def _copy(self, source, dest):
        if not self._has_key(source):
            raise KeyError(source)
        with map_boto_exceptions(key=source):
                self.bucket.copy_key(self.prefix + dest, self.bucket.name, self.prefix + source)

    def _put(self, key, data):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            k.set_contents_from_string(
                data, **self.__upload_args()
            )
            return key

    def _put_file(self, key, file):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            k.set_contents_from_file(
                file, **self.__upload_args()
            )
            return key

    def _put_filename(self, key, filename):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            k.set_contents_from_filename(
                filename, **self.__upload_args()
            )
            return key

    def _url_for(self, key):
        k = self.__new_key(key)
        with map_boto_exceptions(key=key):
            return k.generate_url(expires_in=self.url_valid_time,
                                  query_auth=False)
