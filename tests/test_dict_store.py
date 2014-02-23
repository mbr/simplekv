#!/usr/bin/env python
# coding=utf8
from simplekv.memory import DictStore

from basic_store import BasicStore
from idgens import UUIDGen, HashGen

import pytest


class TestDictStore(BasicStore, UUIDGen, HashGen):
    @pytest.fixture
    def store(self):
        return DictStore()
