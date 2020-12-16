#!/usr/bin/env bash

set -e

read -p 'Stack name: ' stackname
read -sp 'Database password: ' dbpassword

source ../.env

echo "Using env variables"
echo "APT_FRONTEND_URL $APT_FRONTEND_URL"
echo "IDP_METADATA_URL $IDP_METADATA_URL"
echo "JWT_SECRET $JWT_SECRET"
echo "FASTAPI_HOST $FASTAPI_HOST"

echo

read -p "Continue (y/n)? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

echo "Deploying"

aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name $stackname \
  --tags Project=nasa-apt \
  --parameter-overrides \
      DBName=nasadb \
      DBUser=masteruser \
      DBPassword=$dbpassword \
      JWTSecret=$JWT_SECRET \
      APTFrontendUrl=$APT_FRONTEND_URL \
      IDPMetadataUrl=$IDP_METADATA_URL \
      FastapiHost=$FASTAPI_HOST \
      ElasticsearchDomainName=nasadb-$stackname \
  --region us-east-1 --capabilities CAPABILITY_IAM
