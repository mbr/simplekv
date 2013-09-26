#!/usr/bin/env python
# coding=utf8

import os
import sys

from setuptools import setup, find_packages

# the "test" command has been removed, as the test discovery does not
# work with the packaged unittest in python 2.7 (it's missing the
# unittest2.collector)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='simplekv',
      version='0.7.1.dev1',
      description='A key-value storage for binary data, support many '\
                  'backends.',
      long_description=read('README.rst'),
      keywords='key-value-store storage key-value db database s3 gs boto'\
               'memcache cache',
      author='Marc Brinkmann',
      author_email='git@marcbrinkmann.de',
      url='http://github.com/mbr/simplekv',
      license='MIT',
      packages=find_packages(exclude=['test']),
      py_modules=[],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Database',
          'Topic :: Software Development :: Libraries',
      ]
     )
