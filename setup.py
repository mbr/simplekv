#!/usr/bin/env python
# coding=utf8

import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='simplekv',
      version='0.10.1.dev1',
      description=('A key-value storage for binary data, support many '
                   'backends.'),
      long_description=read('README.rst'),
      author='Marc Brinkmann',
      author_email='git@marcbrinkmann.de',
      url='http://github.com/mbr/simplekv',
      license='MIT',
      packages=find_packages(exclude=['test']),
      install_requires=[],
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ])
