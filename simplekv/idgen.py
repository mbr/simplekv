#!/usr/bin/env python
# coding=utf8

import hashlib
import os
import tempfile
import uuid


class HashMixin(object):
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
