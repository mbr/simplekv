#!/usr/bin/env python
# coding=utf8

import hashlib
import hmac
import tempfile


class _HMACFileReader(object):
    def __init__(self, hm, source):
        self.hm = hm
        self.source = source

        # "preload" buffer
        self.buffer = source.read(self.hm.digest_size)
        if not len(self.buffer) == self.hm.digest_size:
            raise VerificationException('Source does not contain HMAC hash '\
                                        '(too small)')

    def read(self, n=None):
        if '' == self.buffer or 0 == n:
            return ''

        new_read = self.source.read(n) if None != n else self.source.read()
        finished = (None == n or len(new_read) != n)
        self.buffer += new_read

        offset = min(n, len(self.buffer) - self.hm.digest_size)
        rv, self.buffer = self.buffer[:offset], self.buffer[offset:]

        # update hmac
        self.hm.update(rv)

        if finished:
            # check hash
            if not self.buffer == self.hm.digest():
                raise VerificationException('HMAC verification failed.')

        return rv

    def close():
        self.source.close()


class VerificationException(Exception):
    pass
