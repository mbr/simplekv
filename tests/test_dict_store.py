#!/usr/bin/env python
# coding=utf8
from simplekv.memory import DictStore
from simplekv import CopyMoveMixin

from basic_store import BasicStore
from idgens import UUIDGen, HashGen
from test_hmac import HMACDec

import pytest


class TestDictStore(BasicStore, UUIDGen, HashGen, HMACDec):
    @pytest.fixture
    def store(self):
        return DictStore()

    @pytest.fixture()
    def copy_move_store(self):
        class CopyMoveStore(DictStore, CopyMoveMixin):
            pass
        return CopyMoveStore()
