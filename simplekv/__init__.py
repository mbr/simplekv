#!/usr/bin/env python
# coding=utf8

import re

VALID_NON_NUM = r"""\`\!"#$%&'()+,-.<=>?@[]^_{}~"""
VALID_KEY_REGEXP = "^[%s0-9a-zA-Z]+$" % re.escape(VALID_NON_NUM)
VALID_KEY_RE = re.compile(VALID_KEY_REGEXP)

class KeyValueStorage(object):
    """The smallest API supported by all backends.

    Keys are ascii-strings with certain restrictions, guaranteed to be properly
    handled up to a length of at least 256 characters.

    Any function that takes a key as an argument raises a ValueError if the
    key is incorrect.
    """
    def get(self, key):
        """Returns the key data as a string.

        :param key: Key to get

        :raises KeyError: If the key is not valid.
        :raises IOError: If the file could not be read.
        :raises IndexError: If the key was not found.
        """
        self._check_valid_key(key)
        return self._get(key)

    def open(self, key):
        """Open key for reading.

        Returns a read-only file-like object for reading a key.

        :param key: Key to open

        :raises KeyError: If the key is not valid.
        :raises IOError: If the file could not be read.
        :raises IndexError: If the key was not found.
        """
        self._check_valid_key(key)
        return self._open(key)

    def put(self, key, data_or_readable):
        """Store into key

        Stores data into a key, from a string or "somewhat filelike" object.
        If the object has a .read() method, data will be read from it as if it
        was a file, otherwise the result of a str() conversion is stored
        instead.

        Note that the object only needs to support read() and _may_ support
        a fileno() method as well.

        :param key: The key under which the data is to be stored
        :param data_or_readable: Any object (will be converted to string using
        str()) or a "readable" object, i.e. one that has a read() method

        :raises KeyError: If the key is not valid.
        :raises IOError: If storing failed.
        """
        self._check_valid_key(key)
        if hasattr(data_or_readable, 'read'):
            return self._put_readable(key, data_or_readable)
        else:
            return self._put_data(key, str(data_or_readable))

    def put_file(self, key, filename):
        """Store into key from file on disk

        This is a convenience method to allow some backends to implement more
        efficient ways of adding files to a repository (e.g. by simply renaming
        a file instead of copying it).

        Note that the file will be removed in the process. If you need to make
        a copy, pass the opened file to :func:`put`.

        :param key: The key under which the data is to be stored
        :param filename: The path to a file that is to be moved into the
        backend.

        :raises KeyError: If the key is not valid.
        :raises IOError: If there was a problem moving the file in.
        """
        with file(filename, 'rb') as f:
            self.put(key, f)

    def _check_valid_key(self, key):
        if not VALID_KEY_RE.match(key):
            raise ValueError('%r contains illegal characters' % key)
