#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest

playhouse = pytest.importorskip('playhouse')
peewee = pytest.importorskip('peewee')

from playhouse.db_url import connect
from peewee import OperationalError

from simplekv.db.peewee import PeeweeStore

from basic_store import BasicStore


# FIXME: for local testing, this needs configurable dsns
class TestPeeweeStore(BasicStore):
    DSNS = [
        ('pymysql',
         'mysql://travis:@localhost/simplekv_test'),
        ('psycopg2',
         'postgresql://postgres:@127.0.0.1/simplekv_test'),
        ('sqlite3',
         'sqlite:///:memory:')
    ]

    @pytest.fixture(params=DSNS, ids=[v[0] for v in DSNS])
    def engine(self, request):
        module_name, dsn = request.param
        # check module is available
        pytest.importorskip(module_name)
        engine = connect(dsn)
        try:
            engine.connect()
        except OperationalError:
            pytest.skip('could not connect to database {}'.format(dsn))
        return engine

    @pytest.yield_fixture
    def store(self, engine):
        store = PeeweeStore(engine, 'simplekv_test')

        yield store

        store.model.drop_table(fail_silently=False)
