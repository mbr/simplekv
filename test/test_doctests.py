#!/usr/bin/env python
# coding=utf8

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import doctest

import simplekv.idgen


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(simplekv.idgen))
    return tests
