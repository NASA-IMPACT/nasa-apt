# nasa-apt

### nasa-apt-api-dev development branch

**Version:** Development Branch - v2.4.0

Code and issues relevant to the NASA APT project

## Components: 
- [FastAPI](https://fastapi.tiangolo.com/): provides the routes/methods for the REST API. Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation, [SQLAlchemy](https://www.sqlalchemy.org/) for database connection and ORM and [PyLatex](https://jeltef.github.io/PyLaTeX/current/) for Latex/PDF document generation
- [Postgresql](https://www.postgresql.org/): Database where ATBD and ATBD Version content is stored
- [opensearch](https://www.opensearch.co/opensearch/): Document indexing to provide full-text searching of ATBD documents

### Diagram
![Backend Architecture Diagram](adr/APT-infrastructure.jpg)

### AWS Deployment: 
The API is deployed to AWS using [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/home.html). To get started with CDK you will need to have `npm` installed. Follow the steps in the link above to get started. 

To deploy a new APT API stack, copy the `.env.sample` file to your workstation. 
Required values in the `.env` file are: 
- `APT_FRONTEND_URL`. This is the URL where the frontend is deployed. Necessary for the email notifications to build the correct links.
- `NOTIFICATIONS_FROM`. This is the email address from which notification emails will be set. Either the address or the domain must have been [verified in SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-domains.html)

Optional values in the `.env` file are: 
- `PROJECT_NAME`. Value will be used to identify the CDK stack and generated resources in AWS. Defaults to `nasa-apt-api`
- `STAGE`. This value will be used to identify the CDK stack and generated resources in AWS. Defaults to `dev`
- `API_VERSION_STRING`. This value will be prepended to all API routes, and __must__ start with a `/`. Defaults to `/v1`
- `OWNER` and `CLIENT`. These values are used for tagging resources in AWS for billing and tracing purposes.
- `VPC_ID`. If provided the generated AWS resources will be placed within this VPC, otherwise a new VPC will be created for the STACK. 
- `S3_BUCKET`. The name of the S3 bucket to store files images and PDFs for the APT application. If provided, this value must be unique within AWS, otherwise the stack will fail to create. 


To deploy a new stack run: 
```bash
git clone https://github.com/NASA-IMPACT/nasa-apt.git

pip install -e .[deploy] # (use ".[deploy]", with quotation marks if on mac)

cdk list # optional - verify that all required pacakges are correctly installed

cdk deploy ${PROJECT_NAME}-lambda-${STAGE} # use the `--profile ${PROFILE_NAME}` flag if using a non-default AWS account
```
eg:
```bash
cdk deploy nasa-apt-api-lambda-dev --profile <AWS_PROFILe>
```
The output of this command will contain the URL endpoint of the REST API, as well as the ARN of the database secrets, which will be used in the next step. 


## Database changes

Database changes and migrations are managed via [sqitch](https://sqitch.org/).
You can find a nice outline of managing Postgres migrations with Sqitch [here](https://sqitch.org/docs/manual/sqitchtutorial/)
This project uses a Sqitch Docker image referencing some local files in order to manage migrations.
As an example, to add a table we could run the following from the project root.

To create a Sqitch migration named `somechange`

```shell script
cd db
./sqitch add somechange --requires previouschange -n 'Change the database in some way'
```

This creates new empty `somechange.sql` scripts in the `deploy`, `revert` and `verify` directories.
You can then update the `somechange.sql` script in the `deploy` directory with the necessary change. Be sure to also include all necessary data migration operations in the `/deploy/` script. 

See the Sqitch [documentation](https://sqitch.org/docs/manual/sqitchtutorial) for more details on change dependencies and validation.

Sqitch migrations must be manually applied the database in AWS. When deploying a stack for the first time, to prepare the database you will need the database secrets to access the database. 

These can be found using the CLI: 
```bash
aws secretsmanager get-secret-value --secret-id ${STACK_NAME}-database-secrets # you can also use the secrets ARN from the output of the `cdk deploy` command as the value of the `--secret-id` flag
```
or throught the AWS console, by going to AWS Secrets manager and selecting the instance corresponding to the recently deployed CDK stack. 

The secrets value needed to setup the database are: 
- `HOST`
- `USERNAME`
- `PASSWORD`
- `DBNAME` (should be default value of `nasadb`)
- `PORT` (should be default value of `5432`) 

With these values the DB migration can be applied as follows (requires Docker): 
```bash
cd db
./sqitch deploy --verify db:pg://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${DBNAME} 
```

Once the database has been setup, any migrations must also be manually applied to the database using the above command. 

Optionally, some of the test fixture data can be loaded with the following command (requires [psql](https://www.postgresql.org/docs/13/app-psql.html), recommended **only** for dev/staging environemnts):

```bash
cd db # if not already in `/cd`
psql 'postgres://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${DBNAME}?options=--search_path%3dapt' -f ./testData.sql
```

The database has Point-In-Time recovery available by default - which allows you to recover the state of the database from any point in the last 7 days. 
(More info on how to restore the database from backup coming soon.)

## Local development
The API can be run locally for development purposes. To run locally, run: 
```bash
docker-compose up --build
```
This will create several docker containers: one for the Postgres database, one for the REST API, one for the opensearch instance and one for a Localstack instance, which mocks AWS resources locally. 

The Localstack container will instantiate a cognito service. The cognito service is a PAID feature of localstack, so you'll need an API key for a localstack PRO account as an env variable (in the `.env` file): 

```bash
LOCALSTACK_API_KEY=...
```

When running the front-end locally, the `sign-up` functionality will still point to the hosted UI - meaning that it will not be possible to sign up. To mitigate this, users will be created when spinning up the APIl.

The following test users will be created (all with the same password: `Password123!`)
- Carlos Curator (email: `curator@apt.com`)
- Olivia Owner (email: `owner@apt.com`)
- Andre Author (email: `author1@apt.com`)
- Anita Author (email: `author2@apt.com`)
- Allison Author (email: `author3@apt.com`)
- Ricardo Reviewer (email: `reviewer1@apt.com`)
- Ronald Reviewer (email: `reviwer2@apt.com`)
- Rita Reviewer (email: `reviewer3@apt.com`)

In order to authenticated with the locally running instance of cognito, the frontend needs to know the User Pool ID and the User Pool Client ID to authenticate against. These values will be printed in the output of the locally running API, but can also be accessed with the following commands: 

```bash
# Grabs user pool id - won't produce any output
pool_id=$(AWS_REGION=us-east-1 aws --endpoint-url http://localhost:4566 cognito-idp list-user-pools --no-sign-request --max-results 100 | jq -rc '.UserPools[0].Id')

# Grab app client id and formats the output
AWS_REGION=us-east-1 aws --endpoint-url http://localhost:4566 cognito-idp list-user-pool-clients --user-pool-id $pool_id  --no-sign-request --max-results 10 | jq -rc '.UserPoolClients[0] | {ClientId: .ClientId, UserPoolId: .UserPoolId}'
```

Populate the `UserPoolId` and `ClientId` values into `ui-config.js`. Restart the `ui` service: `docker-compose restart ui`

Upon spinning up, all necessary database migrations (see below) will be run, and the database will be pre-populated with a test ATBD, which has 2 versions, one with status `Published` and one with status `Draft`. The opensearch instance will not be populated with data until an ATBD gets published or the published ATBD gets its minor version bumped. 

After running for the first time you can drop the `--build` flag (this flag forces the docker image to be re-built).

You can stop running the API with `ctrl+C` and `docker-compose down`. To clear out the volumes and remove the data that gets persisted between sessions, use `docker-compose down --volumes`. 

Locally, the resources will be available at the following endpoints: 

- The REST API is accessible via [http://localhost:8000](http://localhost:8000).
- Autogenerated docs for the REST API is accessible at [http://localhost:8000/docs](http://localhost:8000/docs).

For debugging purposes the data storage resources are available: 
- The Localstack (AWS) resources are accessible via [http://localhost:4566](http://localhost:4566)
- The opensearch instance is accessible via [http://localhost:9200](http://localhost:9200)
- The Postgres DB is accessible via the username/password/host/port/dbname combo: `masteruser/password/localhost/5432/nasadb`

Note: when running the API locally, localstack mocks the SES implementation, meaning it won't actually send any notification emails. However the content and subject of these emails will appear in the localstack docker container logs. 

## Role Based Access: 
An important aspect of the APT API is the restriction of access to document operations depending on application role. Users are divided into 2 groups at the application level: `Curators` and `Contributors`. `Curators` are admin-like users who approve or deny requested stage transitions of ATBDs and manage the users assigned to ATBDs. `Contributors` are users that can be assigned to ATBDs. `Contributors` are divided into 3 groups at the ATBD level: `owner`, or `Lead Author`, `authors` and `reviewers`. 

User authentication in managed by AWS Cognito. When users sign up they will not be assigned to any group, until someone goes through the AWS console to the User Pool for the API and adds the user to either one of the `curator` or `contributor` group. Once a user is part of either group, they will be able to view, and create/update documents, as permitted by their role.

## Contributing
This repo is set to use `pre-commit` to run *my-py*, *flake8*, *pydocstring* and *black* ("uncompromising Python code formatter") when commiting new code.

```bash
pip install -e .[dev] # use ".[dev]" with quotation marks if on mac

pre-commit install
```

```
$ git add .
$ git commit -m'fix a really important thing'
black....................................................................Passed
Flake8...................................................................Passed
Verifying PEP257 Compliance..............................................Passed
mypy.....................................................................Passed
[precommit cc12c5a] fix a really important thing
 ```

## API V1 --> V2

A number of changes were made to the API from it's first iteration:

1. Enable efficient and straightforward (developer friendly) querying and updating of ATBD document versions

    Previously the API was build with [PostgREST](https://postgrest.org/en/stable/), an incredible tool which just needs to be pointed to an existing database, and will generate a REST API that manages foreign key relations and authentication. This was a great way to get the project up and running with very little code, but because the queries were automatically generated, customizing the access patterns to retrieve an entire document quickly became very complex. Additionally, implementing queries beyond simple CRUD operations required complex Postgres functions, which are difficult to debug. 

    The mitigate the above problems we decided to re-implement the API using FastAPI. While this means we have to re-implement CRUD operations ourselves, we now have much finer grained control over data I/O operations. We are able to implement custom queries/operations, as well as custom data validation and formatting and eventually custom authorization logic. 

2. Enable ATBD document versioning

    In order to implement ATBD document versioning we revisited the database structure in Postgres. The data was highly normalized (accross half a dozen differen foreign key relations) which entailed huge complexity for implementing versioning, as creating a new version of a document would have required duplicating table records accross all of these tables. Instead the data was denormzalied into a single `atbd_versions` table - meaning that a new version can be creating with a single record duplication. 

    Since we had already made the decision to use FastAPI we implemented input data validation using Pydantic. Given that, previously, the data was often deeply nested within the highly normalized tables, denormalizing the table and implementing validation with Pydnatic is just as strict, if not stricter, than the data validation that was previously being performed.

3. Enable tighter development cycles by streamlining API deployment process
    
    Previously the API was deployed using a cloudformation template. Migrating to CDK allows us to use Python code to define and provision AWS resources. We can also update any part of the application with a single `cdk deploy` command, wherease before, ECS images had to be updated separately from the Cloudformation stack, depending on what changes were required. 

4. Reduce API response latency and overhead, increase scalability and error traceability
    
    Previously the API was running in ECS instances. The images were difficult to debug as the logs were not readily available, and did not scale as readily as Lambda functions. Using [Mangum](https://pypi.org/project/mangum/) we can wrap our FastAPI app with a single line of code to make it compatible with the Lambda runtime environment. This results in an API that is readily scalable and only incurs costs proportinally to its usage. Lastly we benefit from the Lambda monitoring and logging functionality made available through Cloudwatch. 


## Notes

The PDF serialization service supports unicode characters in text mode. The service uses the font `Latin Modern Math` which has a good coverage of unicode math symbols. See a list of symobls here: https://ctan.math.illinois.edu/macros/latex/contrib/unicode-math/unimath-symbols.pdf
A symbol which is not covered by the font will be rendered as a blank space. Unicode characters used in LaTeX math mode will not be rendered.

## Releases

**A new release should be created every time there's a merge to master.**

Releases are tied to a version number and created manually using GH's releases page.
The version in this README should be increased according to [semver](https://semver.org/) and the release tag should follow the format `v<major>.<minor>.<patch>`, ex: `v2.0.1`.
The release description should have a [changelog](https://gist.github.com/vgeorge/e6fd828987b2f7d62a447df2bd132c4a) with "Features", "Improvements" and "Fixes".

# License

This project is licensed under **The MIT License (MIT)**, see the [LICENSE](LICENSE) file for more details.
