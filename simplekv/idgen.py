#!/usr/bin/env python
# coding=utf8

"""
In cases where you want to generate IDs automatically, decorators are
available. These should be the outermost decorators, as they change the
signature of some of the put methods slightly.

>>> from simplekv.memory import DictStore
>>> from simplekv.idgen import HashDecorator
>>>
>>> store = HashDecorator(DictStore())
>>>
>>> key = store.put(None, b'my_data') #  note the passing of 'None' as key
>>> print(key)
ab0c15b6029fdffce16b393f2d27ca839a76249e
"""

import hashlib
import os
import tempfile
import uuid

from .decorator import StoreDecorator


class HashDecorator(StoreDecorator):
    """Hash function decorator

    Overrides :meth:`.KeyValueStore.put` and :meth:`.KeyValueStore.put_file`.
    If a key of *None* is passed, the data/file is hashed using
    ``hashfunc``, which defaults to *hashlib.sha1*. """

    def __init__(self, decorated_store, hashfunc=hashlib.sha1, template='{}'):
        self.hashfunc = hashfunc
        self._template = template
        super(HashDecorator, self).__init__(decorated_store)

    def put(self, key, data, *args, **kwargs):
        if not key:
            key = self._template.format(self.hashfunc(data).hexdigest())

        return self._dstore.put(key, data, *args, **kwargs)

    def put_file(self, key, file, *args, **kwargs):
        bufsize = 1024 * 1024
        phash = self.hashfunc()

        if not key:
            if isinstance(file, str):
                with open(file, 'rb') as source:
                    while True:
                        buf = source.read(bufsize)
                        phash.update(buf)

                        if len(buf) < bufsize:
                            break

                    return self._dstore.put_file(
                        self._template.format(phash.hexdigest()),
                        file, *args, **kwargs)
            else:
                tmpfile = tempfile.NamedTemporaryFile(delete=False)
                try:
                    while True:
                        buf = file.read(bufsize)
                        phash.update(buf)
                        tmpfile.write(buf)

                        if len(buf) < bufsize:
                            break

                    tmpfile.close()
                    return self._dstore.put_file(
                        self._template.format(phash.hexdigest()),
                        tmpfile.name, *args, **kwargs
                    )
                finally:
                    try:
                        os.unlink(tmpfile.name)
                    except OSError as e:
                        if 2 == e.errno:
                            pass  # file already gone
                        else:
                            raise
        return self._dstore.put_file(key, file, *args, **kwargs)


class UUIDDecorator(StoreDecorator):
    """UUID generating decorator

    Overrides :meth:`.KeyValueStore.put` and :meth:`.KeyValueStore.put_file`.
    If a key of *None* is passed, a new UUID will be generated as the key. The
    attribute `uuidfunc` determines which UUID-function to use and defaults to
    'uuid1'.

    .. note::
       There seems to be a bug in the uuid module that prevents initializing
       `uuidfunc` too early. For that reason, it is a string that will be
       looked up using :func:`getattr` on the :mod:`uuid` module.
    """
    # for strange reasons, this needs to be looked up as late as possible
    uuidfunc = 'uuid1'

    def __init__(self, store, template='{}'):
        super(UUIDDecorator, self).__init__(store)
        self._template = template

    def put(self, key, data, *args, **kwargs):
        if not key:
            key = str(getattr(uuid, self.uuidfunc)())

        return self._dstore.put(
            self._template.format(key), data, *args, **kwargs
        )

    def put_file(self, key, file, *args, **kwargs):
        if not key:
            key = str(getattr(uuid, self.uuidfunc)())

        return self._dstore.put_file(
            self._template.format(key), file, *args, **kwargs
        )
