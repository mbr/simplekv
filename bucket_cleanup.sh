#!/bin/sh -x
s3cmd rb -r `s3cmd ls | grep -e 's3://testrun.*' -o`
