#!/usr/bin/env python
# coding=utf8

import os
import shutil

from . import KeyValueStore, UrlMixin
from ._compat import url_quote


class FilesystemStore(KeyValueStore, UrlMixin):
    """Store data in files on the filesystem.

    The *FilesystemStore* stores every value as its own file on the filesystem,
    all under a common directory.

    Any call to :meth:`.url_for` will result in a `file://`-URL pointing
    towards the internal storage to be generated.
    """
    def __init__(self, root, perm=None, **kwargs):
        """Initialize new FilesystemStore

        When files are created, they will receive permissions depending on the
        current umask if *perm* is `None`. Otherwise, permissions are set
        expliicitly.

        Note that when using :func:`put_file` with a filename, an attempt to
        move the file will be made. Permissions and ownership of the file will
        be preserved that way. If *perm* is set, permissions will be changed.

        :param root: the base directory for the store
        :param perm: the permissions for files in the filesystem store
        """
        super(FilesystemStore, self).__init__(**kwargs)
        self.root = root
        self.perm = perm
        self.bufsize = 1024 * 1024  # 1m

    def _build_filename(self, key):
        return os.path.abspath(os.path.join(self.root, key))

    def _delete(self, key):
        try:
            os.unlink(self._build_filename(key))
        except OSError as e:
            if not e.errno == 2:
                raise

    def _fix_permissions(self, filename):
        current_umask = os.umask(0)
        os.umask(current_umask)

        perm = self.perm
        if self.perm is None:
            perm = 0o666 & (0o777 ^ current_umask)

        os.chmod(filename, perm)

    def _has_key(self, key):
        return os.path.exists(self._build_filename(key))

    def _open(self, key):
        try:
            f = open(self._build_filename(key), 'rb')
            return f
        except IOError as e:
            if 2 == e.errno:
                raise KeyError(key)
            else:
                raise

    def _put_file(self, key, file):
        bufsize = self.bufsize

        target = self._build_filename(key)

        with open(target, 'wb') as f:
            while True:
                buf = file.read(bufsize)
                f.write(buf)
                if len(buf) < bufsize:
                    break

        # when using umask, correct permissions are automatically applied
        # only chmod is necessary
        if self.perm is not None:
            self._fix_permissions(target)

        return key

    def _put_filename(self, key, filename):
        target = self._build_filename(key)
        shutil.move(filename, target)

        # we do not know the permissions of the source file, rectify
        self._fix_permissions(target)
        return key

    def _url_for(self, key):
        full = os.path.abspath(self._build_filename(key))
        parts = full.split(os.sep)
        location = '/'.join(url_quote(p, safe='') for p in parts)
        return 'file://' + location

    def keys(self):
        return os.listdir(self.root)

    def iter_keys(self):
        return iter(self.keys())


class WebFilesystemStore(FilesystemStore):
    """FilesystemStore that supports generating URLs suitable for web
    applications. Most common use is to make the *root* directory of the
    filesystem store available through a webserver. Example:

    >>> from simplekv.fs import WebFilesystemStore
    >>> webserver_url_prefix = 'https://some.domain.invalid/files/'
    >>> webserver_root = '/var/www/some.domain.invalid/www-data/files/'
    >>> store = WebFilesystemStore(webserver_root, webserver_url_prefix)
    >>> print(store.url_for('some_key'))
    https://some.domain.invalid/files/some_key

    Note that the prefix is simply prepended to the relative URL for the key.
    It therefore, in most cases, must include a trailing slash.

    *url_prefix* may also be a callable, in which case it gets called with the
    filestore and key as an argument and should return an url_prefix.

    >>> from simplekv.fs import WebFilesystemStore
    >>> webserver_url_prefix = 'https://some.domain.invalid/files/'
    >>> webserver_root = '/var/www/some.domain.invalid/www-data/files/'
    >>> prefix_func = lambda store, key: webserver_url_prefix
    >>> store = WebFilesystemStore(webserver_root, prefix_func)
    >>> print(store.url_for('some_key'))
    https://some.domain.invalid/files/some_key
    """
    def __init__(self, root, url_prefix, **kwargs):
        """Initialize new WebFilesystemStore.

        :param root: see :func:`simplekv.FilesystemStore.__init__`
        :param url_prefix: will get prepended to every url generated with
                           url_for.
        """
        super(WebFilesystemStore, self).__init__(root, **kwargs)

        self.url_prefix = url_prefix

    def _url_for(self, key):
        rel = key

        if callable(self.url_prefix):
            stem = self.url_prefix(self, key)
        else:
            stem = self.url_prefix
        return stem + url_quote(rel, safe='')
