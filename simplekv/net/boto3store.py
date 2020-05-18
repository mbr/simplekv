#!/usr/bin/env python
# coding=utf8

from .._compat import imap
from .. import KeyValueStore, CopyMixin
from contextlib import contextmanager
from shutil import copyfileobj
import io


@contextmanager
def map_boto3_exceptions(key=None, exc_pass=()):
    """Map boto3-specific exceptions to the simplekv-API."""
    from botocore.exceptions import ClientError

    try:
        yield
    except ClientError as ex:
        if ex.response['Error']['Code'] == 'NoSuchKey':
            raise KeyError(key)
        raise IOError(str(ex))


# todo: test this more thoroughly
class Boto3SimpleKeyFile(io.RawIOBase):
    # see: https://alexwlchan.net/2019/02/working-with-large-s3-objects/
    # author: Alex Chan, license: MIT
    def __init__(self, s3_object):
        self.s3_object = s3_object
        self.position = 0

    def __repr__(self):
        return "<%s s3_object=%r>" % (type(self).__name__, self.s3_object)

    @property
    def size(self):
        return self.s3_object.content_length

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.position = offset
        elif whence == io.SEEK_CUR:
            self.position += offset
        elif whence == io.SEEK_END:
            self.position = self.size + offset
        else:
            raise ValueError("invalid whence (%r, should be %d, %d, %d)" % (
                whence, io.SEEK_SET, io.SEEK_CUR, io.SEEK_END
            ))

        return self.position

    def seekable(self):
        return True

    def read(self, size=-1):
        if size == -1:
            # Read to the end of the file
            range_header = "bytes=%d-" % self.position
            self.seek(offset=0, whence=io.SEEK_END)
        else:
            new_position = self.position + size

            # If we're going to read beyond the end of the object, return
            # the entire object.
            if new_position >= self.size:
                return self.read()

            range_header = "bytes=%d-%d" % (self.position, new_position - 1)
            self.seek(offset=size, whence=io.SEEK_CUR)

        return self.s3_object.get(Range=range_header)["Body"].read()

    def readable(self):
        return True


class Boto3Store(KeyValueStore, CopyMixin):
    def __init__(self, bucket, prefix=''):
        self.prefix = prefix.strip().lstrip('/')
        self.bucket = bucket

    def __new_object(self, name):
        return self.bucket.Object(self.prefix + name)

    def iter_keys(self, prefix=u""):
        with map_boto3_exceptions():
            prefix_len = len(self.prefix)
            return imap(lambda k: k.key[prefix_len:],
                        self.bucket.objects.filter(Prefix=self.prefix + prefix))

    def _has_key(self, key):
        from botocore.exceptions import ClientError
        with map_boto3_exceptions(key=key):
            try:
                self.bucket.Object(self.prefix + key).load()
            except ClientError as error:
                if error.response['Error']['Code'] == '404':
                    return False
                raise error
            return True

    def _delete(self, key):
        self.bucket.Object(self.prefix + key).delete()

    def _get(self, key):
        obj = self.__new_object(key)
        with map_boto3_exceptions(key=key):
            obj = obj.get()
            return obj['Body'].read()

    def _get_file(self, key, file):
        obj = self.__new_object(key)
        with map_boto3_exceptions(key=key):
            obj = obj.get()
            return copyfileobj(obj['Body'], file)

    def _get_filename(self, key, filename):
        obj = self.__new_object(key)
        with map_boto3_exceptions(key=key):
            obj = obj.get()
            with open(filename, 'wb') as file:
                return copyfileobj(obj['Body'], file)

    def _open(self, key):
        obj = self.__new_object(key)
        with map_boto3_exceptions(key=key):
            return Boto3SimpleKeyFile(obj)

    def _copy(self, source, dest):
        if not self._has_key(source):
            raise KeyError(source)
        obj = self.__new_object(dest)
        with map_boto3_exceptions(key=source):
            obj.copy_from(CopySource=self.bucket.name + '/' + self.prefix + source)

    def _put(self, key, data):
        obj = self.__new_object(key)
        with map_boto3_exceptions(key=key):
            obj.put(Body=data)
            return key

    def _put_file(self, key, file):
        obj = self.__new_object(key)
        with map_boto3_exceptions(key=key):
            obj.put(Body=file)
            return key

    def _put_filename(self, key, filename):
        with open(filename, 'rb') as file:
            return self._put(key, file)
