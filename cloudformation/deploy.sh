#!/usr/bin/env bash

set -e

read -p 'Stack name: ' stackname
read -sp 'Database password: ' dbpassword

aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name $stackname \
  --tags Project=nasa-apt \
  --parameter-overrides \
      DBName=nasadb \
      DBUser=masteruser \
      DBPassword=$dbpassword \
      ElasticsearchDomainName=nasadb-$stackname \
  --region us-east-1 --capabilities CAPABILITY_IAM
