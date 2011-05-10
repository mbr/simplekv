#!/usr/bin/env python
# coding=utf8

class KeyValueStorage(object):
    """The smallest API supported by all backends.

    Keys are ascii-strings and guaranteed to be properly handled up to a
    length of at least 256 characters.
    """
    def get(key):
        """Returns the key data as a string.

        Raises a `KeyError` if the key does not exist.
        """
        raise NotImplementedError

    def put(key, data_or_filelike):
        """Store into key

        Stores data into a key, from a string or filelike object. If the object
        has a .read() method, data will be read from it as if it was a file,
        otherwise the result of a str() conversion is stored instead.

        Raises an `IOError` if storing failed.
        """
        raise NotImplementedError

    def open(key):
        """Open key for reading.

        Returns a read-only file-like object for reading a key.

        Raises an `IOError` if storing failed.
        """
        raise NotImplementedError
