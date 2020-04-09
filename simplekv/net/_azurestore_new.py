"""
This implements the AzureBlockBlobStore for `azure-storage-blob~=12`
"""
import io
from contextlib import contextmanager

from .._compat import PY2
from .. import KeyValueStore

from ._azurestore_common import (
    _byte_buffer_md5,
    _file_md5,
    lazy_property,
    LAZY_PROPERTY_ATTR_PREFIX,
)


if PY2:

    def _blobname_to_texttype(name):
        """
        Convert the str `name` to unicode
        """
        return name.decode('utf-8')
else:

    def _blobname_to_texttype(name):
        return name


@contextmanager
def map_azure_exceptions(key=None, error_codes_pass=()):
    """Map Azure-specific exceptions to the simplekv-API."""
    from azure.core.exceptions import AzureError

    try:
        yield
    except AzureError as ex:
        error_code = getattr(ex, "error_code", None)
        if error_code is not None and error_code in error_codes_pass:
            return
        if error_code == "BlobNotFound":
            raise KeyError(key)
        raise IOError(str(ex))


class AzureBlockBlobStore(KeyValueStore):
    def __init__(
        self,
        conn_string=None,
        container=None,
        public=False,
        create_if_missing=True,
        max_connections=2,
        max_block_size=None,
        max_single_put_size=None,
        checksum=False,
        socket_timeout=None,
    ):
        """
        Note that socket_timeout is unused;
        it only exist for backward compatibility.
        """
        self.conn_string = conn_string
        self.container = container
        self.public = public
        self.create_if_missing = create_if_missing
        self.max_connections = max_connections
        self.max_block_size = max_block_size
        self.max_single_put_size = max_single_put_size
        self.checksum = checksum

    # Using @lazy_property will (re-)create block_blob_service instance needed.
    # Together with the __getstate__ implementation below, this allows
    # AzureBlockBlobStore to be pickled, even if
    # azure.storage.blob.BlockBlobService does not support pickling.
    @lazy_property
    def blob_container_client(self):
        from azure.storage.blob import BlobServiceClient

        kwargs = {}
        if self.max_single_put_size:
            kwargs["max_single_put_size"] = self.max_single_put_size

        if self.max_block_size:
            kwargs["max_block_size"] = self.max_block_size

        service_client = BlobServiceClient.from_connection_string(
            self.conn_string, **kwargs
        )
        container_client = service_client.get_container_client(self.container)
        if self.create_if_missing:
            with map_azure_exceptions(error_codes_pass=("ContainerAlreadyExists")):
                container_client.create_container(
                    public_access="container" if self.public else None
                )
        return container_client

    def _delete(self, key):
        with map_azure_exceptions(key, error_codes_pass=("BlobNotFound",)):
            self.blob_container_client.delete_blob(key)

    def _get(self, key):
        with map_azure_exceptions(key):
            blob_client = self.blob_container_client.get_blob_client(key)
            downloader = blob_client.download_blob(max_concurrency=self.max_connections)
            return downloader.readall()

    def _has_key(self, key):
        blob_client = self.blob_container_client.get_blob_client(key)
        with map_azure_exceptions(key, ("BlobNotFound",)):
            blob_client.get_blob_properties()
            return True
        return False

    def iter_keys(self, prefix=None):
        with map_azure_exceptions():
            blobs = self.blob_container_client.list_blobs(name_starts_with=prefix)

        def gen_names():
            with map_azure_exceptions():
                for blob in blobs:
                    yield _blobname_to_texttype(blob.name)
        return gen_names()

    def iter_prefixes(self, delimiter, prefix=u""):
        return (
            _blobname_to_texttype(blob_prefix.name)
            for blob_prefix in self.blob_container_client.walk_blobs(
                name_starts_with=prefix, delimiter=delimiter
            )
        )

    def _open(self, key):
        with map_azure_exceptions(key):
            blob_client = self.blob_container_client.get_blob_client(key)
            return IOInterface(blob_client, self.max_connections)

    def _put(self, key, data):
        from azure.storage.blob import ContentSettings

        if self.checksum:
            content_settings = ContentSettings(
                content_md5=_byte_buffer_md5(data, b64encode=False)
            )
        else:
            content_settings = ContentSettings()

        with map_azure_exceptions(key):
            blob_client = self.blob_container_client.get_blob_client(key)

            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=content_settings,
                max_concurrency=self.max_connections,
            )
        return key

    def _put_file(self, key, file):
        from azure.storage.blob import ContentSettings

        if self.checksum:
            content_settings = ContentSettings(content_md5=_file_md5(file, b64encode=False))
        else:
            content_settings = ContentSettings()

        with map_azure_exceptions(key):
            blob_client = self.blob_container_client.get_blob_client(key)

            blob_client.upload_blob(
                file,
                overwrite=True,
                content_settings=content_settings,
                max_concurrency=self.max_connections,
            )
        return key

    def _get_file(self, key, file):
        with map_azure_exceptions(key):
            blob_client = self.blob_container_client.get_blob_client(key)
            downloader = blob_client.download_blob(max_concurrency=self.max_connections)
            downloader.readinto(file)

    def __getstate__(self):
        # keep all of __dict__, except lazy properties:
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith(LAZY_PROPERTY_ATTR_PREFIX)
        }


class IOInterface(io.BufferedIOBase):
    """
    Class which provides a file-like interface to selectively read from a blob in the blob store.
    """

    def __init__(self, blob_client, max_connections):
        super(IOInterface, self).__init__()
        self.blob_client = blob_client
        self.max_connections = max_connections

        blob_props = self.blob_client.get_blob_properties()
        self.size = blob_props.size
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
        downloader = self.blob_client.download_blob(
            self.pos, size, max_concurrency=self.max_connections
        )
        b = downloader.readall()
        self.pos += len(b)
        return b

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
