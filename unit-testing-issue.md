After working through some testing options for several days, here are some thoughts on testing strategies going forward: 

# Background:

The obvious tradeoff in testing is that the closer an environemnt replicates the production environment the less likely the tests are to let errors through, _however_ the closer the environment replicates the production environment, the more time consuming/expensive it is to set up and run the tests. 

Examples in increasing order of fidelity to production environment (and therefore in increasing quality of coverage): 
## 1. Tests run against functions from the code base locally, with all external resources mocked. 

- These would be considered "proper" unit tests, as they only test functional logic "units" against various inputs and output. 
- There are different strategies to mock the external resources such as:
    - [wiremock](https://wiremock.org/docs/record-playback/), which first "records" the results of API calls in plain json, and then later intercepts requests made to the external API and serves the responses from the locally stored plain json, without having to contact the external API (playback)
    - [moto](https://github.com/spulec/moto) which provides a wrapper around the boto3 objects to serve mocked responses to boto calls
### Pros: 
- Tests can be run locally and quickly (and therefore can be run often)
### Cons: 
- More work work to setup and maintain, as it requires knowledge of the behaviour of the external resources and the tests have to be updated if any of the interactions with the external resources are modified.
- Test coverage is not as extensive, as these test internal logic units of the API rather than interactions between backend components. With a backend as complex at APT's, bugs most often arise in the interaction between components (eg: an S3 request might be well formulated and therefore pass the test for retrieving a file when run against a mocked S3 isntance, while the actual file itself would be missing in the real API for some other reason.)

## 2. Tests run against a dockerized instance of the API with other resources mocked as needed (eg: localstack for cognito + s3, a postgres docker instance, an elasticsearch docker instance)
These are closer to integration tests as they allow for the testing of the integration betweeen components (eg: does the API correclty handle the updated data model returned by the database)

### Pros: 
- Allows for testing of integration between components locally, and therefore cheap and quickly 
- Allows for testing the _behaviour_ of the API rather than the individual logic blocks. This has the advantage that team memebers (and especially stakeholders) who are less familiar with the codebase can still write test cases in the form of user stories, eg: As a **_user_** I want **_the curator to be notified_** when **_I mark my document as ready for review_** in order to **_be able to publish my ATBD quickly and efficiently_**.
### Cons: 
- Because the resources are mocked on an ad-hock basis (eg: using a Postgres docker instance in a locally running container), there is no guarantee that any of the resources will behave the same way in AWS as they do locally. 
- Mocking the various resources requires work to configure, and sometimes requires modifications to the code base itself, in order for the code base to work when deployed in AWS and in tests (eg: the boto3 client has to be instantiated with an endpoint URL when making the requests to locally mocked resources, but no when instantiated in a lambda function)

### 2.1. Mock _all_ of the AWS resources using localstack. 
Localstack is a paid service that provies mocked AWS services locally. In order to avoid re-inventing the wheel, we stand a better of change of having accurately mocked services which remain up-to-date with AWS updates if we entrust it to a team paid to do just that. However the reality of it is that localstack is a product still very much under developement, with several key features missing/workarounds necessary, which we will further explore later. 

## 3. Tests run against resources deployed to an AWS environment (proper integration tests):
### Pros: 
- The tests will most accurately reflect the behaviour of the API, since the resources that the tests get run against will be identical to the resources in production.
- There is no need to invest time and effort into mocking resources' behaviour, or running them locally, as the production deployment script can be re-used to generate a testing stack.
- It allows us to test our infrastructure deployment code as well. For example: an update to the infrastructure configuration that accidentally revokes access permissions from one resource to another would not be caught by testing the code logic units or by testing the API against locally mocked resources, but would be caught when run against resources deployed to AWS.
### Cons: 
- Resources can take a very long time to deploy, on the order of 10s of minutes (and sometimes even longer to destroy). This can also be expensive both in AWS, but also in CI/CD processes, which are often paid for by the minute and would have to wait idly for the resources to finish deploying in AWS.
- Account limits can be hit by deploying many instances of the same resources, which, in the best case scenario blocks further testing, but in the worst case scenario blocks other projects from deploying the resources they might need 
- We don't have CI/CD access to NASA MCP account, which means that there are some idiosyncratic behaviours from the production environment that we will still not be able to replicate, despite running our tests against resources deployed in AWS. 

# Compromise: 
The ideal testing strategy we adopt will likely be a mixture of the above strategies. Local running "logical unit" tests (unit tests) can be run quickly and often (on each commit using commit hooks, for example) and full integration tests run against resources deployed in AWS only when merging to develop, for example. 

This allows for the adoption of a 2 layered TDD: developers define the unit tests for their proposed features and clients/partners at impact can provide behavioural tests for the integartion tests. See [this comment](https://github.com/developmentseed/how/issues/363#issuecomment-1084691741) for further thoughts on TDD and involvement from partners.

# Current setup:

# Localstack:
The reason I started to investigate localstack is beacuse of the promise of localstack being able to better replicate the bahaviour of AWS resources than we could. Since we already paying for a localstack pro membership for mockign the cognito user pools, why not take full advantage of the features offered.

## Pre-requisites: 
- [CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html): `npm install -g aws-cdk@v1.x` (APT is currently deployed using CDK v1, but it should be soon migrated to CDK v2)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)
- [Localstack AWS CLI](https://github.com/localstack/awscli-local) (awslocal): wraps around the AWS CLI and ensures that all commands are executed against localstack, typically acessible at `http://localhost:4566`
- [CDK Loacal](https://github.com/localstack/aws-cdk-local): Is to CDK what AWSLocal is to the AWS CLI

## Setup: 
Localstack can be easily instantiated with docker-compose:

`docker-compose.yml`: 
```yaml
localstack:
    image: localstack/localstack:latest
    environment:
      - LOCALSTACK_API_KEY=${LOCALSTACK_API_KEY}
      - DEBUG=1
      - LAMBDA_EXECUTOR=docker
      - LAMBDA_REMOTE_DOCKER=0
      - HOST_TMP_FOLDER=${TMPDIR:-/tmp}
      - LAMBDA_DOCKER_FLAGS=-e AWS_DEFAULT_REGION=us-east-1 -e AWS_RESOURCES_ENDPOINT=http://localstack:4566
      - HOST_TMP_FOLDER=${TMPDIR:-/tmp}/localstack
      - DOCKER_SOCK=unix:///var/run/docker.sock
    ports:
      - "53:53" # only required for Pro (DNS)
      - "53:53/udp" # only required for Pro (DNS)
      - "443:443" # only required for Pro (LocalStack HTTPS Edge Proxy)
      - "4510-4559:4510-4559" # external service port range
      - "4566:4566" # LocalStack Edge Proxy
    volumes:
      - "${TMPDIR:-/tmp}/localstack:/tmp/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"
```

And then started up using: 
```bash
docker compose up --build localstack
```
Once localstack is up and running, the CDK stack can to be deployed to it. _In theory_ you _should_ be able do: 
```bash
cdklocal deploy nasa-apt-api-lambda-{STAGE}
```
And you have an APT backend up and running, ready to be bootstrapped (run database migrations using `sqitch` and load test data). 

Deploying the CDK stack, running the DB migrations and loading test data can be easily automated by mounting a volume that contains a bash script with the above commands to `docker-entrypoint-initaws.d`:
```yaml
    volumes:
        - "./startup_scripts/:/docker-entrypoint-initaws.d/startup_scripts/"
```

eg: `statup_script/bootstrap.sh`: 
```bash
# install libs
npm install -g aws-cdk@v1.x aws-cdk-local 
pip install awscli-local

# app code gets mounted at /tmp
cd /tmp 
# install deployment libs
pip install ".[dev,deploy]"

# bootstrap CDK localstack
cdklocal bootstrap --require-approval never
# deploy stack to local
cdklocal deploy nasa-apt-api-lambda-staging --require-approval never

# run database migrations
cd db
./sqitch deploy db:pg://masteruser:password@localhost:4512/nasadb
cd ..

# load fixture data (if needed)
./fixture_data/bootstrap_localstack.sh

# print API ID
awslocal apigatewayv2 get-apis --query 'Items[0].ApiId' 
```

The API endpoint should be accessibe at: 
```bash
http://localhost:4566/restapis/{API_ID}/local/_user_request_/v2/atbds
```

As you can see, the promise of localstack is to provide a local testing environment that more accurately (although not 100%) reflects the behaviour and interactions of AWS resources with less work to configure that our current local strategy