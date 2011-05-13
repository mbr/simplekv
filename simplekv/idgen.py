#!/usr/bin/env python
# coding=utf8

"""
In cases where you want to generate IDs automatically, mixins are available.
When deriving your custom store class, ensure that the mixins are first in the
method resolution order. Example:

>>> from simplekv.memory import DictStore
>>> from simplekv.idgen import HashMixin
>>>
>>> class Sha1Store(HashMixin, DictStore):
...     pass  # note: sha1 is the default hash function for HashMixin
...
>>>
>>> store = Sha1Store()
>>>
>>> key = store.put(None, 'my_data') #  note the passing of 'None' as key
>>> print key
ab0c15b6029fdffce16b393f2d27ca839a76249e
"""

import hashlib
import os
import tempfile
import uuid


class HashMixin(object):
    """Hash function mixin

    Overrides :func:`put` and :func:`put_file`. If a key of *None* is passed,
    the data/file is hashed using :func:`hashfunc`, which defaults to
    *hashlib.sha1*.
    """

    hashfunc = hashlib.sha1

    def put(self, key, data):
        if not key:
            key = self.hashfunc(data).hexdigest()

        return super(HashMixin, self).put(key, data)

    def put_file(self, key, file):
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

                    return super(HashMixin, self).put_file(
                        phash.hexdigest(),
                        file)
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
                    return super(HashMixin, self).put_file(
                        phash.hexdigest(),
                        tmpfile.name
                    )
                finally:
                    os.unlink(tmpfile.name)
        return super(HashMixin, self).put_file(key, file)


class UUIDMixin(object):
    """UUID generating mixin

    Overrides :func:`put` and :func:`put_file`. If a key of *None* is passed,
    a new UUID will be generated as the key. The attribute `uuidfunc`
    determines which UUID-function to use and defaults to 'uuid1'.

    .. note::
       There seems to be a bug in the uuid module that prevents initializing
       `uuidfunc` too early. For that reason, it is a string that will be
       looked up using :func:`getattr` on the :mod:`uuid` module.
    """

    uuidfunc = 'uuid1'  # for strange reasons, this needs to be looked up
                        # as late as possible

    def put(self, key, data):
        if not key:
            key = str(getattr(uuid, self.uuidfunc)())

        return super(UUIDMixin, self).put(key, data)

    def put_file(self, key, file):
        if not key:
            key = str(getattr(uuid, self.uuidfunc)())

        return super(UUIDMixin, self).put_file(key, file)
