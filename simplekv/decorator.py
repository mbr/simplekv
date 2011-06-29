#!/usr/bin/env python
# coding=utf8


class StoreDecorator(object):
    """Base class for store decorators.

    The default implementation will use :func:`getattr` to pass through all
    attribute/method requests to an underlying object stored as
    :attr:`_dstore`. It will also pass through the :attr:`__getattr__` and
    :attr:`__contains__` python special methods.
    """
    def __init__(self, store):
        self._dstore = store

    def __getattr__(self, attr):
        return getattr(self._dstore, attr)

    def __contains__(self, *args, **kwargs):
        return self._dstore.__contains__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._dstore.__iter__(*args, **kwargs)
