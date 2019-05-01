#!/bin/bash
read -sp 'Database password: ' dbpassword
aws cloudformation deploy --template-file cloudformation.yaml --stack-name \
nasa-apt --tags Project=nasa-apt --parameter-overrides \
DBName=nasadb DBUser=masteruser DBPassword=$dbpassword \
--region us-east-1 --capabilities CAPABILITY_IAM
