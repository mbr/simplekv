# coding: utf8

import pytest


def test_url_for_for_generates_url_for(urlstore):
    k = 'uk'
    urlstore.put(k, 'v')
    assert type(urlstore.url_for(k)), str


def test_url_for_generation_does_not_check_exists(urlstore):
    urlstore.url_for('does_not_exist_at_all')


def test_url_for_generation_checks_valid_key(urlstore):
    with pytest.raises(ValueError):
        urlstore.url_for(u'ä')

    with pytest.raises(ValueError):
        urlstore.url_for('/')

    with pytest.raises(ValueError):
        urlstore.url_for('\x00')

    with pytest.raises(ValueError):
        urlstore.url_for('*')

    with pytest.raises(ValueError):
        urlstore.url_for('')
