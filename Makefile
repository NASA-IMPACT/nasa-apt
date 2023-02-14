COMPOSE=docker-compose -f docker-compose.yml
pool_id := $(shell AWS_REGION=us-east-1 aws --endpoint-url http://localhost:4566 cognito-idp list-user-pools --no-sign-request --max-results 100 | jq -rc '.UserPools[0].Id')

services:
	$(COMPOSE) up -d --remove-orphans \
		db mail opensearch localstack

all: services
	$(COMPOSE) up api ui worker

worker: services
	$(COMPOSE) up ui worker

cognito-config:
	@AWS_REGION=us-east-1 aws --endpoint-url http://localhost:4566 cognito-idp list-user-pool-clients --user-pool-id $(pool_id)  --no-sign-request --max-results 10 | jq -rc '.UserPoolClients[0] | {ClientId: .ClientId, UserPoolId: .UserPoolId}'

stop:
	$(COMPOSE) stop

restart-worker:
	$(COMPOSE) restart worker