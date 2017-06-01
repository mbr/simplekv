#!/usr/bin/env python
# coding=utf8

from uuid import uuid4 as uuid

import pytest
pymongo = pytest.importorskip('pymongo')

from simplekv.db.mongo import MongoStore
from basic_store import BasicStore
from conftest import ExtendedKeyspaceTests
from simplekv import ExtendedKeyspaceMixin


class TestMongoDB(BasicStore):
    @pytest.fixture
    def db_name(self):
        return '_simplekv_test_{}'.format(uuid())

    @pytest.yield_fixture
    def store(self, db_name):
        try:
            conn = pymongo.MongoClient()
        except pymongo.errors.ConnectionFailure:
            pytest.skip('could not connect to mongodb')
        yield MongoStore(conn[db_name], 'simplekv-tests')
        conn.drop_database(db_name)


class TestExtendedKeyspaceDictStore(TestMongoDB, ExtendedKeyspaceTests):
    @pytest.fixture
    def store(self, db_name):
        class ExtendedKeyspaceStore(ExtendedKeyspaceMixin, MongoStore):
            pass
        try:
            conn = pymongo.MongoClient()
        except pymongo.errors.ConnectionFailure:
            pytest.skip('could not connect to mongodb')
        yield ExtendedKeyspaceStore(conn[db_name], 'simplekv-tests')
        conn.drop_database(db_name)
