#!/usr/bin/env python
# coding=utf8

import pytest

sqlalchemy = pytest.importorskip('sqlalchemy')
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import OperationalError

from simplekv.db.sql import SQLAlchemyStore

from basic_store import BasicStore


# FIXME: for local testing, this needs configurable dsns
class TestSQLAlchemyStore(BasicStore):
    DSNS = [
        ('pymysql',
         'mysql+pymysql://travis:@localhost/simplekv_test'),
        ('psycopg2',
         'postgresql+psycopg2://postgres:@127.0.0.1/simplekv_test'),
        ('sqlite3',
         'sqlite:///:memory:')
    ]

    @pytest.fixture(params=DSNS, ids=[v[0] for v in DSNS])
    def engine(self, request):
        module_name, dsn = request.param
        # check module is available
        pytest.importorskip(module_name)
        engine = create_engine(dsn)
        try:
            engine.connect()
        except OperationalError:
            pytest.skip('could not connect to database {}'.format(dsn))
        return engine

    @pytest.yield_fixture
    def store(self, engine):
        metadata = MetaData(bind=engine)
        store = SQLAlchemyStore(engine, metadata, 'simplekv_test')

        # create table
        store.table.create()

        yield store

        metadata.drop_all()
