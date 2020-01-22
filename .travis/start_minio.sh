#!/usr/bin/env bash

set -e
set -x

wget -O ~/minio https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x ~/minio

export MINIO_ACCESS_KEY=minio
export MINIO_SECRET_KEY=miniostorage

mkdir -p ~/s3

~/minio --version
~/minio server ~/s3 &
