#!/usr/bin/env bash

set -e
set -x

go get -u github.com/minio/minio

export MINIO_ACCESS_KEY=fjeiowgjepgmeovsdvdasda
export MINIO_SECRET_KEY=fasduiqwrzqwoitghdnvdfjknbvylkmdiofjkw

mkdir -p ~/s3
minio server ~/s3 > /tmp/minio.log 2>&1 &
