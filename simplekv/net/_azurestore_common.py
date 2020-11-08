"""
Internal utilities for aztorestore_old and azurestore_new
"""

import hashlib
import base64


def _file_md5(file_, b64encode=True):
    """
    Compute the md5 digest of a file in base64 encoding.

    For ``b64encode``, returns the base64 encoded string; otherwise, returns the
    bytes directly.
    """
    md5 = hashlib.md5()
    chunk_size = 128 * md5.block_size
    for chunk in iter(lambda: file_.read(chunk_size), b""):
        md5.update(chunk)
    file_.seek(0)
    byte_digest = md5.digest()
    if b64encode:
        return base64.b64encode(byte_digest).decode()
    else:
        return byte_digest


def _filename_md5(filename, b64encode=True):
    """
    Compute the md5 digest of a file in base64 encoding.
    """
    with open(filename, "rb") as f:
        return _file_md5(f, b64encode=b64encode)


def _byte_buffer_md5(buffer_, b64encode=True):
    """
    Computes the md5 digest of a byte buffer in base64 encoding.
    """
    md5 = hashlib.md5(buffer_)
    byte_digest = md5.digest()
    if b64encode:
        return base64.b64encode(byte_digest).decode()
    else:
        return byte_digest
