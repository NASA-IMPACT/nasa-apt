aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 552819999234.dkr.ecr.us-east-1.amazonaws.com
docker build -t 552819999234.dkr.ecr.us-east-1.amazonaws.com/nasa-apt/saml/fastapi fastapi/.
docker push 552819999234.dkr.ecr.us-east-1.amazonaws.com/nasa-apt/saml/fastapi
aws ecs update-service --force-new-deployment --cluster nasa-apt-v5-prod-ECSCluster-tNTELpBkxUy7 --service nasa-apt-v5-prod-svc-fastapi --region us-east-1
