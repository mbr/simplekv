#!/usr/bin/env python
# coding=utf8

from setuptools import setup
import sys

if sys.version_info < (2, 7):
    tests_require = ['unittest2', 'mock']
    test_suite = 'unittest2.collector'
else:
    tests_require = ['mock']
    test_suite = 'unittest.collector'

setup(name='simplekv',
      version='0.3dev',
      description='A simple key-value storage for binary data.',
      author='Marc Brinkmann',
      author_email='git@marcbrinkmann.de',
      url='http://github.com/mbr/simplekv',
      packages=['simplekv'],
      py_modules=[],
      tests_require=tests_require,
      test_suite='unittest2.collector'
     )
