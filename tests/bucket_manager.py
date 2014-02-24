#!/usr/bin/env python
# coding=utf8

from simplekv._compat import ConfigParser
from contextlib import contextmanager
from uuid import uuid4 as uuid

import pytest

boto = pytest.importorskip('boto')


@contextmanager
def boto_bucket(access_key, secret_key, connect_func='connect_s3',
                bucket_name=None):
        conn = getattr(boto, connect_func)(access_key, secret_key)

        name = bucket_name or 'testrun-bucket-{}'.format(uuid())
        bucket = conn.create_bucket(name)

        yield bucket

        for key in bucket.list():
            key.delete()
        bucket.delete()


def load_boto_credentials():
    # loaded from the same place tox.ini. here's a sample
    #
    # [my-s3]
    # access_key=foo
    # secret_key=bar
    # connect_func=connect_s3
    #
    # [my-gs]
    # access_key=foo
    # secret_key=bar
    # connect_func=connect_gs
    cfg_fn = 'boto_credentials.ini'

    parser = ConfigParser()
    if not parser.read(cfg_fn):
        pytest.skip('file {} not found'.format(cfg_fn))

    for section in parser.sections():
        yield {
            'access_key': parser.get(section, 'access_key'),
            'secret_key': parser.get(section, 'secret_key'),
            'connect_func': parser.get(section, 'connect_func'),
        }


boto_credentials = list(load_boto_credentials())
