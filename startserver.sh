#!/bin/bash
docker-compose up & while ! nc -z localhost 4572; do sleep 1; done;
sleep 10;
aws --endpoint-url=http://localhost:4572 s3 mb s3://figures
aws --endpoint-url=http://localhost:4572 s3api put-bucket-acl --bucket figures --acl public-read
aws --endpoint-url=http://localhost:4572 s3 cp ./figures/fullmoon.jpg s3://figures

