#!/bin/sh -x

# this will stop you from growing old before 1000 s3 tests finish
# requires pytest-xdist
py.test -f -n 10 --boxed tests/test_boto_store.py
