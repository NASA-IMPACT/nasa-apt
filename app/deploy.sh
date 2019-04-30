#!/bin/bash
export REACT_APP_ATBD_JSON_BUCKET=$(aws cloudformation list-exports --region us-east-1 --query "Exports[?Name==\`nasa-apt-AtbdJsonBucket\`].Value" --output text)
echo $REACT_APP_ATBD_JSON_BUCKET
export REACT_APP_ATBD_BUCKET=$(aws cloudformation list-exports --region us-east-1 --query "Exports[?Name==\`nasa-apt-AtbdBucket\`].Value" --output text)
echo $REACT_APP_ATBD_BUCKET
export REACT_APP_API_URL=$(aws cloudformation list-exports --region us-east-1 --query "Exports[?Name==\`nasa-apt-PostgRESTEndpoint\`].Value" --output text)
echo $REACT_APP_API_URL
yarn build
aws s3 sync build/ $(aws cloudformation list-exports --region us-east-1 --query "Exports[?Name==\`nasa-apt-WebsiteBucket\`].Value" --output text)

