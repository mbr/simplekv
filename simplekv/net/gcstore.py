import io
from typing import Union
from ._net_common import lazy_property, LAZY_PROPERTY_ATTR_PREFIX
from .. import KeyValueStore
from google.auth.credentials import Credentials
from google.cloud.storage import Client, Blob
from google.cloud.exceptions import NotFound, GoogleCloudError


class GoogleCloudStore(KeyValueStore):
    def __init__(
        self,
        credentials: Union[str, Credentials],
        bucket_name: str,
        create_if_missing=True,
        bucket_creation_location="EUROPE-WEST3",
        project=None,
    ):
        """A store using `Google Cloud storage <https://cloud.google.com/storage>`_ as a backend.

        :param: credentials: Either the path to a `credentials JSON file
                             <https://cloud.google.com/docs/authentication/production>`_
                             or an instance of *google.auth.credentials.Credentials*.
        :param bucket_name: Name of the bucket the blobs will be stored in.
                            Needs to follow the `naming conventions
                            <https://cloud.google.com/storage/docs/naming-buckets>`_.
        :param create_if_missing: Creates the bucket if it doesn't exist yet.
                                  The bucket's ACL will be the default `ACL
                                  <https://cloud.google.com/storage/docs/access-control/lists#default>`_.
        :param bucket_creation_location: Location to create the bucket in,
                                       if the bucket doesn't exist yet. One of `Bucket locations
                                       <https://cloud.google.com/storage/docs/locations>`_.
        :param project: name of the project. If credentials JSON is passed,
                        value of *project* will be ignored as it can be inferred.
        """
        self._credentials = credentials
        self.bucket_name = bucket_name
        self.create_if_missing = create_if_missing
        self.bucket_creation_location = bucket_creation_location
        self.project_name = project

    # this exists to allow the store to be pickled even though the underlying gc client
    # doesn't support pickling. We make pickling work by omitting self.client from __getstate__
    # and just (re)creating the client & bucket when they're used (again).
    @lazy_property
    def _bucket(self):
        if self.create_if_missing and not self._client.lookup_bucket(self.bucket_name):
            return self._client.create_bucket(
                bucket_or_name=self.bucket_name, location=self.bucket_creation_location
            )
        else:
            # will raise an error if bucket not found
            return self._client.get_bucket(self.bucket_name)

    @lazy_property
    def _client(self):
        if type(self._credentials) == str:
            return Client.from_service_account_json(self._credentials)
        else:
            return Client(credentials=self._credentials, project=self.project_name)

    def _delete(self, key: str):
        try:
            self._bucket.delete_blob(key)
        except NotFound:
            # simpleKV doesn't raise an error if key doesn't exist
            pass

    def _get(self, key: str):
        blob = Blob(name=key, bucket=self._bucket)
        try:
            blob_bytes = blob.download_as_bytes()
        except NotFound:
            raise KeyError(key)
        return blob_bytes

    def _get_file(self, key: str, file):
        blob = Blob(name=key, bucket=self._bucket)
        try:
            blob.download_to_file(file)
        except NotFound:
            raise KeyError

    def _has_key(self, key: str):
        return Blob(key, self._bucket).exists()

    def iter_keys(self, prefix=""):
        return (blob.name for blob in self._bucket.list_blobs(prefix=prefix))

    def _open(self, key: str):
        blob = Blob(key, self._bucket)
        if not blob.exists():
            raise KeyError
        return IOInterface(blob)

    def _put(self, key: str, data: bytes):
        blob = Blob(key, self._bucket)
        if type(data) != bytes:
            raise IOError(f"data has to be of type 'bytes', not {type(data)}")
        blob.upload_from_string(data, content_type="application/octet-stream")
        return key

    def _put_file(self, key, file):
        blob = Blob(key, self._bucket)
        try:
            blob.upload_from_file(file_obj=file)
        except GoogleCloudError:
            raise IOError
        return key

    # skips two items: bucket & client.
    # These will be recreated after unpickling through the lazy_property decoorator
    def __getstate__(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith(LAZY_PROPERTY_ATTR_PREFIX)
        }


class IOInterface(io.BufferedIOBase):
    """
    Class which provides a file-like interface to selectively read from a blob in the bucket.
    """

    def __init__(self, blob: Blob):
        super(IOInterface, self).__init__()
        self.blob = blob

        if blob.size is None:
            blob.reload()
        self.size = blob.size
        self.pos = 0

    def tell(self):
        """Returns he current offset as int. Always >= 0."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        return self.pos

    def read(self, size=-1):
        """Returns 'size' amount of bytes or less if there is no more data.
        If no size is given all data is returned. size can be >= 0."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        max_size = max(0, self.size - self.pos)
        if size < 0 or size > max_size:
            size = max_size
        if size == 0:
            return b""
        blob_bytes = self.blob.download_as_bytes(
            start=self.pos, end=self.pos + size - 1
        )
        self.pos += len(blob_bytes)
        return blob_bytes

    def seek(self, offset, whence=0):
        """Move to a new offset either relative or absolute. whence=0 is
        absolute, whence=1 is relative, whence=2 is relative to the end.

        Any relative or absolute seek operation which would result in a
        negative position is undefined and that case can be ignored
        in the implementation.

        Any seek operation which moves the position after the stream
        should succeed. tell() should report that position and read()
        should return an empty bytes object."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        if whence == 0:
            if offset < 0:
                raise IOError("seek would move position outside the file")
            self.pos = offset
        elif whence == 1:
            if self.pos + offset < 0:
                raise IOError("seek would move position outside the file")
            self.pos += offset
        elif whence == 2:
            if self.size + offset < 0:
                raise IOError("seek would move position outside the file")
            self.pos = self.size + offset
        return self.pos

    def seekable(self):
        return True

    def readable(self):
        return True
