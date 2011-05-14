#!/usr/bin/env python
# coding=utf8

import os
import shutil
import urllib

from . import UrlKeyValueStore


class FilesystemStore(UrlKeyValueStore):
    """Store data in files on the filesystem.

    The *FilesystemStore* stores every value as its own file on the filesystem,
    all under a common directory.

    Any call to :func:`url_for` will result in a `file://`-URL pointing towards
    the internal storage to be generated.
    """
    def __init__(self, root, **kwargs):
        """Initialize new FilesystemStore

        :param root: the base directory for the store
        """
        super(FilesystemStore, self).__init__(**kwargs)
        self.root = root
        self.bufsize = 1024 * 1024  # 1m

    def _build_filename(self, key):
        return os.path.join(self.root, key)

    def _delete(self, key):
        try:
            os.unlink(self._build_filename(key))
        except OSError, e:
            if not e.errno == 2:
                raise

    def _has_key(self, key):
        return os.path.exists(self._build_filename(key))

    def _open(self, key):
        try:
            f = open(self._build_filename(key), 'rb')
            return f
        except IOError, e:
            if 2 == e.errno:
                raise KeyError(key)
            else:
                raise

    def _put(self, key, data):
        with file(self._build_filename(key), 'wb') as f:
            f.write(data)

        return key

    def _put_file(self, key, file):
        bufsize = self.bufsize
        with open(self._build_filename(key), 'wb') as f:
            while True:
                buf = file.read(bufsize)
                f.write(buf)
                if len(buf) < bufsize:
                    break

        return key

    def _put_filename(self, key, filename):
        shutil.move(filename, self._build_filename(key))
        return key

    def _url_for(self, key):
        full = os.path.abspath(self._build_filename(key))
        parts = full.split(os.sep)
        location = '/'.join(urllib.quote(p, safe='') for p in parts)
        return 'file://' + location

    def keys(self):
        return os.listdir(self.root)

    def iter_keys(self):
        return iter(self.keys())
