#!/usr/bin/env python
# coding=utf8

import pytest

sqlalchemy = pytest.importorskip('sqlalchemy')
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import StaticPool

from simplekv.db.sql import SQLAlchemyStore

from basic_store import BasicStore
from conftest import ExtendedKeyspaceTests
from simplekv.contrib import ExtendedKeyspaceMixin


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
        engine = create_engine(dsn, poolclass=StaticPool)
        try:
            engine.connect()
        except OperationalError:
            pytest.skip('could not connect to database {}'.format(dsn))
        return engine

    @pytest.fixture
    def store(self, engine):
        metadata = MetaData()
        store = SQLAlchemyStore(engine, metadata, 'simplekv_test')
        # create table
        store.table.create(bind=engine)
        yield store
        metadata.drop_all(bind=engine)


class TestExtendedKeyspaceSQLAlchemyStore(TestSQLAlchemyStore,
                                          ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self, engine):
        class ExtendedKeyspaceStore(ExtendedKeyspaceMixin, SQLAlchemyStore):
            pass
        metadata = MetaData()
        store = ExtendedKeyspaceStore(engine, metadata, 'simplekv_test')
        # create table
        store.table.create(bind=engine)
        yield store
        metadata.drop_all(bind=engine)
