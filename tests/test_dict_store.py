#!/usr/bin/env python
# coding=utf8
from simplekv.memory import DictStore

from basic_store import BasicStore

import pytest


class TestDictStore(BasicStore):
    @pytest.fixture
    def store(self):
        return DictStore()
