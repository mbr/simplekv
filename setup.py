#!/usr/bin/env python
# coding=utf8

import os
import sys

from setuptools import setup

if sys.version_info < (2, 7):
    tests_require = ['unittest2', 'mock']
    test_suite = 'unittest2.collector'
else:
    tests_require = ['mock']
    test_suite = 'unittest.collector'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='simplekv',
      version='0.1',
      description='A simple key-value storage for binary data.',
      long_description=read('README.markdown'),
      keywords='',
      author='Marc Brinkmann',
      author_email='git@marcbrinkmann.de',
      url='http://github.com/mbr/simplekv',
      license='MIT',
      packages=['simplekv'],
      py_modules=[],
      tests_require=tests_require,
      test_suite='unittest2.collector',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Database',
          'Topic :: Software Development :: Libraries',
      ]
     )
