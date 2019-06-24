#!/bin/bash
read -sp 'Database password: ' dbpassword
aws cloudformation deploy --template-file cloudformation.yaml --stack-name \
nasa-apt-staging --tags Project=nasa-apt --parameter-overrides \
DBName=nasadb DBUser=masteruser DBPassword=$dbpassword \
AtbdJsonBucketName=json \
AtbdBucketName=atbd \
FiguresBucketName=figures \
ScriptsBucketName=scripts \
--region us-east-1 --capabilities CAPABILITY_IAM
