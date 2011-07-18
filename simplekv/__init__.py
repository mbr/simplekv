#!/usr/bin/env python
# coding=utf8

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import re

VALID_NON_NUM = r"""\`\!"#$%&'()+,-.<=>?@[]^_{}~"""
VALID_KEY_REGEXP = "^[%s0-9a-zA-Z]+$" % re.escape(VALID_NON_NUM)
"""This regular expression tests if a key is valid. Allowed are all
alphanumeric characters, as well as ``!"`#$%&'()+,-.<=>?@[]^_{}~``."""

VALID_KEY_RE = re.compile(VALID_KEY_REGEXP)
"""A compiled version of :data:`~simplekv.VALID_KEY_REGEXP`."""


class KeyValueStore(object):
    """The smallest API supported by all backends.

    Keys are ascii-strings with certain restrictions, guaranteed to be properly
    handled up to a length of at least 250 characters. Any function that takes
    a key as an argument raises a ValueError if the key is incorrect.

    The regular expression for what constitutes a valid key is available as
    :data:`simplekv.VALID_KEY_REGEXP`.
    """
    def __contains__(self, key):
        """Checks if a key is present

        :param key: The key whose existence should be verified.

        :raises ValueError: If the key is not valid.
        :raises IOError: If there was an error accessing the store.

        :returns: True if the key exists, False otherwise.
        """

        self._check_valid_key(key)
        return self._has_key(key)

    def __iter__(self):
        """Iterate over keys

        :raises IOError: If there was an error accessing the store.
        """
        return self.iter_keys()

    def delete(self, key):
        """Delete key and data associated with it.

        If the key does not exist, no error is reported.

        :raises ValueError: If the key is not valid.
        :raises IOError: If there was an error deleting.
        """
        self._check_valid_key(key)
        return self._delete(key)

    def get(self, key):
        """Returns the key data as a string.

        :param key: Key to get

        :raises ValueError: If the key is not valid.
        :raises IOError: If the file could not be read.
        :raises KeyError: If the key was not found.
        """
        self._check_valid_key(key)
        return self._get(key)

    def get_file(self, key, file):
        """Write contents of key to file

        Like :func:`put_file`, this method allows backends to implement a
        specialized function if data needs to be written to disk or streamed.

        If *file* is a string, contents of *key* are written to a newly
        created file with the filename *file*. Otherwise, the data will be
        written using the *write* method of *file*.

        :param key: The key to be read
        :param file: Output filename or an object with a *write* method.

        :raises ValueError: If the key is not valid.
        :raises IOError: If there was a problem reading or writing data.
        :raises KeyError: If the key was not found.
        """
        self._check_valid_key(key)
        if isinstance(file, str):
            return self._get_filename(key, file)
        else:
            return self._get_file(key, file)

    def iter_keys(self):
        """Return an Iterator over all keys currently in the store, in any
        order.

        :raises IOError: If there was an error accessing the store.
        """
        raise NotImplementedError

    def keys(self):
        """Return a list of keys currently in store, in any order

        :raises IOError: If there was an error accessing the store.
        """
        return list(self.iter_keys())

    def open(self, key):
        """Open key for reading.

        Returns a read-only file-like object for reading a key.

        :param key: Key to open

        :raises ValueError: If the key is not valid.
        :raises IOError: If the file could not be read.
        :raises KeyError: If the key was not found.
        """
        self._check_valid_key(key)
        return self._open(key)

    def put(self, key, data):
        """Store into key from file

        Stores string *data* in *key*.

        :param key: The key under which the data is to be stored
        :param data: Data to be stored into key

        :returns: The key under which data was stored

        :raises ValueError: If the key is not valid.
        :raises IOError: If storing failed or the file could not be read
        """
        self._check_valid_key(key)
        return self._put(key, data)

    def put_file(self, key, file):
        """Store into key from file on disk

        Stores data from a source into key. *file* can either be a string,
        which will be interpretet as a filename, or an object with a *read()*
        method.

        If the passed object has a *fileno()* method, it may be used to speed
        up the operation.

        The file specified by *file*, if it is a filename, may be removed in
        the process, to avoid copying if possible. If you need to make a copy,
        pass the opened file instead.

        :param key: The key under which the data is to be stored
        :param file: A filename or an object with a read method. If a filename,
                     may be removed

        :returns: The key under which data was stored

        :raises ValueError: If the key is not valid.
        :raises IOError: If there was a problem moving the file in.
        """
        if isinstance(file, str):
            return self._put_filename(key, file)
        else:
            return self._put_file(key, file)

    def _check_valid_key(self, key):
        """Checks if a key is valid and raises a ValueError if its not.

        When in need of checking a key for validity, always use this
        method if possible.

        :param key: The key to be checked
        """
        if not VALID_KEY_RE.match(key):
            raise ValueError('%r contains illegal characters' % key)

    def _delete(self, key):
        """Implementation for :meth:`~simplekv.KeyValueStore.delete`. The
        default implementation will simply raise a
        :py:exc:`NotImplementedError`.
        """
        raise NotImplementedError

    def _get(self, key):
        """Implementation for :meth:`~simplekv.KeyValueStore.get`. The default
        implementation will create a :mod:`StringIO`-buffer and then call
        :meth:`~simplekv.KeyValueStore._get_file`.

        :param key: Key to be retrieved
        """
        buf = StringIO()

        self._get_file(key, buf)

        return buf.getvalue()

    def _get_file(self, key, file):
        """Write key to file-like object file. Either this method or
        :meth:`~simplekv.KeyValueStore._get_filename` will be called by
        :meth:`~simplekv.KeyValueStore.get_file`. Note that this method does
        not accept strings.

        :param key: Key to be retrieved
        :param file: File-like object to write to
        """
        source = self.open(key)
        bufsize = 1024 * 1024

        while True:
            buf = source.read(bufsize)
            file.write(buf)

            if len(buf) < bufsize:
                break

    def _get_filename(self, key, filename):
        """Write key to file. Either this method or
        :meth:`~simplekv.KeyValueStore._get_file` will be called by
        :meth:`~simplekv.KeyValueStore.get_file`. This method only accepts
        filenames and will open the file with a mode of ``wb``, then call
        :meth:`~simplekv.KeyValueStore._get_file`.

        :param key: Key to be retrieved
        :param filename: Filename to write to
        """
        with open(filename, 'wb') as dest:
            return self._get_file(key, dest)

    def _has_key(self, key):
        """Default implementation for
        :meth:`~simplekv.KeyValueStore.__contains__`.

        Determines whether or not a key exists by calling
        :meth:`~simplekv.KeyValueStore.keys`.

        :param key: Key to check existance of
        """
        return key in self.keys()

    def _open(self, key):
        """Open key for reading. Default implementation simply raises a
        :exc:`NotImplementedError`.

        :param key: Key to open
        """
        raise NotImplementedError

    def _put(self, key, data):
        """Implementation for :meth:`~simplekv.KeyValueStore.put`. The default
        implementation will create a :mod:`StringIO`-buffer and then call
        :meth:`~simplekv.KeyValueStore._put_file`.

        :param key: Key under which data should be stored
        :param data: Data to be stored
        """
        return self._put_file(key, StringIO(data))

    def _put_file(self, key, file):
        """Store data from file-like object in key. Either this method or
        :meth:`~simplekv.KeyValueStore._put_filename` will be called by
        :meth:`~simplekv.KeyValueStore.put_file`. Note that this method does
        not accept strings.

        The default implementation will simply raise a
        :exc:`NotImplementedError`.

        :param key: Key under which data should be stored
        :param file: File-like object to store data from
        """
        raise NotImplementedError

    def _put_filename(self, key, filename):
        """Store data from file in key. Either this method or
        :meth:`~simplekv.KeyValueStore._put_file` will be called by
        :meth:`~simplekv.KeyValueStore.put_file`. Note that this method does
        not accept strings.

        The default implementation will open the file in ``rb`` mode, then call
        :meth:`~simplekv.KeyValueStore._put_file`.

        :param key: Key under which data should be stored
        :param file: Filename of file to store
        """
        with open(filename, 'rb') as source:
            return self._put_file(key, source)


class UrlKeyValueStore(KeyValueStore):
    """A KeyValueStore that supports getting a download URL for keys.
    """
    def url_for(self, key):
        """Returns a full external URL that can be used to retrieve *key*.

        Does not perform any checks (such as if a key exists), other than
        whether or not *key* is a valid key.

        :param key: The key for which the url is to be generated

        :raises ValueError: If the key is not valid.

        :return: A string containing a URL to access key
        """
        self._check_valid_key(key)
        return self._url_for(key)

    def _url_for(self, key):
        raise NotImplementedError
