# coding: utf8

import pytest


class UrlStore(object):
    def test_url_for_for_generates_url_for(self, store, key, value):
        store.put(key, value)
        assert isinstance(store.url_for(key), basestring)

    def test_url_for_generation_does_not_check_exists(self, store, key):
        store.url_for(key)

    def test_url_for_generation_checks_valid_key(self, store, invalid_key):
        with pytest.raises(ValueError):
            store.url_for(invalid_key)
