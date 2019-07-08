#!/usr/bin/env python
# coding=utf8

import os
import os.path
import shutil

from . import KeyValueStore, UrlMixin, CopyMixin
from ._compat import url_quote, text_type


class FilesystemStore(KeyValueStore, UrlMixin, CopyMixin):
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
        self.root = text_type(root)
        self.perm = perm
        self.bufsize = 1024 * 1024  # 1m

    def _remove_empty_parents(self, path):
        parents = os.path.relpath(path, os.path.abspath(self.root))
        while len(parents) > 0:
            absparent = os.path.join(self.root, parents)
            if os.path.isdir(absparent):
                if len(os.listdir(absparent)) == 0:
                    os.rmdir(absparent)
                else:
                    break
            parents = os.path.dirname(parents)

    def _build_filename(self, key):
        return os.path.abspath(os.path.join(self.root, key))

    def _delete(self, key):
        try:
            targetname = self._build_filename(key)
            os.unlink(targetname)
            self._remove_empty_parents(targetname)
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

    def _copy(self, source, dest):
        try:
            source_file_name = self._build_filename(source)
            dest_file_name = self._build_filename(dest)

            self._ensure_dir_exists(os.path.dirname(dest_file_name))
            shutil.copy(source_file_name, dest_file_name)
            self._fix_permissions(dest_file_name)
            return dest
        except IOError as e:
            if 2 == e.errno:
                raise KeyError(source)
            else:
                raise

    def _ensure_dir_exists(self, path):
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except OSError as e:
                if not os.path.isdir(path):
                    raise e

    def _put_file(self, key, file):
        bufsize = self.bufsize

        target = self._build_filename(key)
        self._ensure_dir_exists(os.path.dirname(target))

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
        self._ensure_dir_exists(os.path.dirname(target))
        shutil.move(filename, target)

        # we do not know the permissions of the source file, rectify
        self._fix_permissions(target)
        return key

    def _url_for(self, key):
        full = os.path.abspath(self._build_filename(key))
        parts = full.split(os.sep)
        location = '/'.join(url_quote(p, safe='') for p in parts)
        return 'file://' + location

    def keys(self, prefix=u""):
        root = os.path.abspath(self.root)
        result = []
        for dp, dn, fn in os.walk(root):
            for f in fn:
                key = os.path.join(dp, f)[len(root) + 1:]
                if key.startswith(prefix):
                    result.append(key)
        return result

    def iter_keys(self, prefix=u""):
        return iter(self.keys(prefix))

    def iter_prefixes(self, delimiter, prefix=u""):
        if delimiter != os.sep:
            return super(FilesystemStore, self).iter_prefixes(
                delimiter,
                prefix,
            )
        return self._iter_prefixes_efficient(delimiter, prefix)

    def _iter_prefixes_efficient(self, delimiter, prefix=u""):
        if delimiter in prefix:
            pos = prefix.rfind(delimiter)
            search_prefix = prefix[:pos]
            path = os.path.join(self.root, search_prefix)
        else:
            search_prefix = None
            path = self.root

        try:
            for k in os.listdir(path):
                subpath = os.path.join(path, k)

                if search_prefix is not None:
                    k = os.path.join(search_prefix, k)

                if os.path.isdir(subpath):
                    k += delimiter

                if k.startswith(prefix):
                    yield k
        except OSError:
            # path does not exists
            pass


class WebFilesystemStore(FilesystemStore):
    """FilesystemStore that supports generating URLs suitable for web
    applications. Most common use is to make the *root* directory of the
    filesystem store available through a webserver. Example:

    >>> from simplekv.fs import WebFilesystemStore
    >>> webserver_url_prefix = 'https://some.domain.invalid/files/'
    >>> webserver_root = '/var/www/some.domain.invalid/www-data/files/'
    >>> store = WebFilesystemStore(webserver_root, webserver_url_prefix)
    >>> print(store.url_for(u'some_key'))
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
    >>> print(store.url_for(u'some_key'))
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
