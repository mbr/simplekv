#!/usr/bin/env python
# coding=utf8

import os
import sys
import tempfile

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

skip_reason = None
try:
    from sqlalchemy import create_engine, MetaData
except ImportError:
    skip_reason = 'SQLAlchemy not installed'
else:
    from simplekv.db.sql import SQLAlchemyStore

from . import SimpleKVTest


@unittest.skipIf(skip_reason, skip_reason)
class TestSQLAlchemy(unittest.TestCase, SimpleKVTest):
    def setUp(self):
        (fd, self.tmpfile) = tempfile.mkstemp('.sqlite', 'simplekv-test')
        self.engine = create_engine('sqlite:///%s' % self.tmpfile)
        self.metadata = MetaData(bind=self.engine)

        self.store = SQLAlchemyStore(self.engine,
                                     self.metadata,
                                     'simplekv_test')

        # create table
        self.store.table.create()

    def tearDown(self):
        os.unlink(self.tmpfile)

    def test_engine(self):
        pass
