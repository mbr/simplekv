# coding: utf8

import pytest


class UrlStore(object):
    def test_url_for_for_generates_url_for(self, store):
        k = 'uk'
        store.put(k, 'v')
        assert type(store.url_for(k)), str

    def test_url_for_generation_does_not_check_exists(self, store):
        store.url_for('does_not_exist_at_all')

    def test_url_for_generation_checks_valid_key(self, store):
        with pytest.raises(ValueError):
            store.url_for(u'ä')

        with pytest.raises(ValueError):
            store.url_for('/')

        with pytest.raises(ValueError):
            store.url_for('\x00')

        with pytest.raises(ValueError):
            store.url_for('*')

        with pytest.raises(ValueError):
            store.url_for('')
