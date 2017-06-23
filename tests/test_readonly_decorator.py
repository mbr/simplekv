#!/usr/bin/env python
# coding=utf8

from simplekv.decorator import ReadOnlyDecorator
from simplekv.memory import DictStore
import pytest


class TestReadOnlyDecorator(object):
    def test_readonly(self):
        store0 = DictStore()
        store0.put(u"file1", b"content")

        store = ReadOnlyDecorator(store0)
        with pytest.raises(AttributeError):
            store.put(u"file1", b"content2")
        with pytest.raises(AttributeError):
            store.delete(u"file1")
        assert store.get(u"file1") == b"content"
        assert u"file1" in store
        assert set(store.keys()) == {u"file1"}
