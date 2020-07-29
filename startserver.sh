#!/usr/bin/env bash

# start local development environment

set -e

PG_PORT=5432
S3_PORT=4572
S3=http://localhost:$S3_PORT # localstack

# .env loading in the shell
dotenv () {
  set -a
  [ -f .env ] && . .env
  set +a
}
dotenv

if [ -z "$FIGURES_S3_BUCKET" ]
then
  echo "error: require FIGURES_S3_BUCKET environment variable (see .env file)"
  exit 1
fi

if [ -z "$PDFS_S3_BUCKET" ]
then
  echo "error: require PDFS_S3_BUCKET environment variable (see .env file)"
  exit 1
fi

docker-compose down

if nc -z localhost $PG_PORT
then
  echo "error: is another postgresql db running?"
  exit 1
fi

docker-compose build

# blocks until given endpoints are accessible over tcp
docker-compose run --rm localstack-ready
docker-compose run --rm db-ready

# start remaining services
docker-compose up --detach

# all the services are up, now create & populate the s3 buckets and the pg database

# localstack: create s3 bucket for figures
aws --endpoint-url=${S3} s3 mb s3://"$FIGURES_S3_BUCKET" --no-sign-request
aws --endpoint-url=${S3} s3api put-bucket-acl --bucket "$FIGURES_S3_BUCKET" --acl public-read-write --no-sign-request &>0
aws --endpoint-url=${S3} s3 cp ./figures/fullmoon.jpg s3://"$FIGURES_S3_BUCKET" --no-sign-request

# localstack: create s3 bucket for pdfs
aws --endpoint-url=${S3} s3 mb s3://"$PDFS_S3_BUCKET" --no-sign-request
aws --endpoint-url=${S3} s3api put-bucket-acl --bucket "$PDFS_S3_BUCKET" --acl public-read-write --no-sign-request &>0

# create db with squitch and load mock data
pushd db
./createdb.sh
./loadTestData.sh
popd

# force postgrest restart to see new schema
docker-compose restart rest-api

# tail the logs
docker-compose logs --follow
