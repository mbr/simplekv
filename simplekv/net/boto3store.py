#!/usr/bin/env python
# coding=utf8

from .._compat import imap
from .. import KeyValueStore, UrlMixin, CopyMixin
from contextlib import contextmanager
from shutil import copyfileobj
import io


@contextmanager
def map_boto3_exceptions(key=None, exc_pass=()):
    """Map boto-specific exceptions to the simplekv-API."""
    from botocore.exceptions import ClientError

    #try:
    #    yield
    #except StorageResponseError as e:
    #    if e.code == 'NoSuchKey':
    #        raise KeyError(key)
    #    raise IOError(str(e))
    except (ClientError,) as e:
        if e.__class__.__name__ not in exc_pass:
            raise IOError(str(e))


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


class Boto3Store(KeyValueStore, UrlMixin, CopyMixin):
    def __init__(self, bucket, prefix='', url_valid_time=0,
                 reduced_redundancy=False, public=False, metadata=None):
        self.prefix = prefix.strip().lstrip('/')
        self.bucket = bucket
        self.reduced_redundancy = reduced_redundancy
        self.public = public
        self.url_valid_time = url_valid_time
        self.metadata = metadata or {}

    def __new_key(self, name):
        # todo: test that this works if the object hasn't been created yet
        key = self.bucket.Object(self.prefix + name)
        key.put(Metadata=self.metadata)
        return key

    def iter_keys(self, prefix=u""):
        with map_boto3_exceptions():
            prefix_len = len(self.prefix)
            return imap(lambda k: k.key[prefix_len:],
                        self.bucket.objects.filter(self.prefix + prefix))

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
        # todo: handle the exception of the key does not exist
        self.bucket.Object(self.prefix + key).delete()

    def _get(self, key):
        k = self.__new_key(key)
        with map_boto3_exceptions(key=key):
            obj = k.get()
            return obj.get()['Body'].read()

    def _get_file(self, key, file):
        k = self.__new_key(key)
        with map_boto3_exceptions(key=key):
            obj = k.get()
            return copyfileobj(obj['Body'], file)

    def _get_filename(self, key, filename):
        k = self.__new_key(key)
        with map_boto3_exceptions(key=key):
            obj = k.get()
            with open(filename, 'wb') as file:
                return copyfileobj(obj['Body'], file)

    def _open(self, key):
        k = self.__new_key(key)
        with map_boto3_exceptions(key=key):
            return Boto3SimpleKeyFile(k)

    def _copy(self, source, dest):
        if not self._has_key(source):
            raise KeyError(source)
        with map_boto3_exceptions(key=source):
            # todo: test that this works as written being relative from self.bucket instead
            # of being hard-coded like https://stackoverflow.com/a/32504096/2722961
            self.bucket.Object(self.prefix + dest).copy_from(CopySource=self.prefix + source)

    def _put(self, key, data):
        k = self.__new_key(key)
        with map_boto3_exceptions(key=key):
            k.put(Body=data)
            return key

    def _put_file(self, key, file):
        k = self.__new_key(key)
        with map_boto3_exceptions(key=key):
            k.put(Body=file)
            return key

    def _put_filename(self, key, filename):
        with open(filename, 'rb') as file:
            return self._put(key, file)

    def _url_for(self, key):
        k = self.__new_key(key)
        params = {
            'Bucket' self.bucket.name,
            'Key': k.key
        }
        # todo: finish this, see: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
        with map_boto3_exceptions(key=key):
            return s3_client.generate_presigned_url('get_object',
                                             Params=params,
                                             ExpiresIn=self.url_valid_time)
