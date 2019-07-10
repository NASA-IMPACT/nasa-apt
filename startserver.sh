#!/bin/bash
docker-compose stop
docker-compose rm -f
docker rmi nasa_apt_db
docker-compose build --no-cache
docker-compose up & while ! nc -z localhost 4572; do sleep 1; done;
sleep 10;
aws --endpoint-url=http://localhost:4572 s3 mb s3://figures --no-sign-request
aws --endpoint-url=http://localhost:4572 s3api put-bucket-acl --bucket figures \
  --acl public-read-write --no-sign-request
aws --endpoint-url=http://localhost:4572 s3 cp \
  ./figures/fullmoon.jpg s3://figures --no-sign-request
aws --endpoint-url=http://localhost:4572 s3 mb s3://nasa-apt-json \
  --no-sign-request
aws --endpoint-url=http://localhost:4572 s3api put-bucket-acl \
  --bucket nasa-apt-json --acl public-read-write --no-sign-request
aws --endpoint-url=http://localhost:4572 s3 mb s3://nasa-apt-atbd \
  --no-sign-request
aws --endpoint-url=http://localhost:4572 s3api put-bucket-acl \
  --bucket nasa-apt-atbd --acl public-read --no-sign-request
cd db
./createdb.sh
./loadTestData.sh
docker-compose stop
sleep 5;
docker-compose up 
