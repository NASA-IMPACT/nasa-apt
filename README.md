# nasa-apt

**Version:** 2.0.0

Code and issues relevant to the NASA APT project

## Components: 
- [FastAPI](https://fastapi.tiangolo.com/): provides the routes/methods for the REST API. Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation, [SQLAlchemy](https://www.sqlalchemy.org/) for database connection and ORM and [PyLatex](https://jeltef.github.io/PyLaTeX/current/) for Latex/PDF document generation
- [Postgresql](https://www.postgresql.org/): Database where ATBD and ATBD Version content is stored
- [ElasticSearch](https://www.elastic.co/elasticsearch/): Document indexing to provide full-text searching of ATBD documents

### AWS Deployment: 
The API is deployed to AWS using [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/home.html). To get started with CDK you will need to have `npm` installed. Follow the steps in the link above to get started. 

To deploy a new APT API stack, copy the `.env.sample` file to your workstation. 
Required values in the `.env` file are: 
- `APT_FRONTEND_URL`. This is the URL where the frontend is deployed. Necessary for the SAML authentication code to redirect the user upon successfull token generation.
-  `IDP_METADATA_URL`. Setting this value to `mock` will cause the API to bypass authentication (and create a valid JWT token whenever you click "login")
- `JWT_SECRET`. This will be the secret key used to sign JWT tokens when authenticating users and validate requests from users. 

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
The output of this command will contain the URL endpoint of the REST API.


## Database changes

Database changes and migrations are managed via [sqitch](https://sqitch.org/).
You can find a nice outline of managing Postgres migrations with Sqitch [here](https://sqitch.org/docs/manual/sqitchtutorial/)
This project uses a Sqitch Docker image referencing some local files in order to manage migrations.
As an example, to add a table we could run the following from the project root.

To create a Sqitch `change`

```shell script
cd db
./sqitch add somechange --requires previouschange -n 'Change the database in some way'
```

This creates new empty `sql` scripts in the `deploy`, `revert` and `verify` directories.
You can then update the `somechange.sql` script in the `deploy` directory with the necessary change.
See the Sqitch [documentation](https://sqitch.org/docs/manual/sqitchtutorial) for more details on change dependencies and validation.

Sqitch migrations must be manually applied the database in AWS. When deploying a stack for the first time, to prepare the database you will need the database secrets to access the database. 

These can be found using the CLI: 
```bash
aws secretsmanager get-secret-value --secret-id ${STACK_NAME}-database-secrets
```
or throught the AWS console, by going to AWS Secrets manager and selecting the instance corresponding to the recently deployed CDK stack. 

The secrets value needed to setup the database are: 
- `HOST`
- `USERNAME`
- `PASSWORD`
- `DBNAME`
- `PORT` (should be default value of `5432`) 

With these values the DB migration can be applied as follows (requires Docker): 
```bash
cd db
./sqitch deploy --verify db:pg://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${DBNAME} 
```

Once the database has been setup, any migrations must also be manually applied to the database using the above command. 
(More info on how to backup, update and restore the database from backup coming soon.)

Optionally, some of the test fixture data can be loaded with the following command (requires [psql](https://www.postgresql.org/docs/13/app-psql.html), recommended **only** for dev/staging environemnts):

```bash
cd db # if not already in `/cd`
psql 'postgres://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${DBNAME}?options=--search_path%3dapt' -f ./testData.sql
```

## Local development
The API can be run locally for development purposes. To run locally, run: 
```bash
docker-compose up --build
```
This will create several docker containers: one for the Postgres database, one for the REST API, one for the ElasticSearch instance and one for a Localstack instance, which mocks AWS resources locally. 

Upon spinning up, all necessary database migrations (see below) will be run, and the database will be pre-populated with a test ATBD, which has 2 versions, one with status `Published` and one with status `Draft`. The ElasticSearch instance will not be populated with data until the ATBD gets updated. 

After running for the first time you can drop the `--build` flag (this flag forces the docker image to be re-built).

You can stop running the API with `ctrl+C` and `docker-compose down`. To clear out the volumes and remove the data that gets persisted between sessions, use `docker-compose down --volumes`. 

Locally, the resources will be available at the following endpoints: 

- The Swagger API documentation is accessible via [http://localhost:8080](http://localhost:8080).
- The REST API is accessible via [http://localhost:8000](http://localhost:8000).

For debugging purposes the data storage resources are available: 
- The Localstack (AWS) resources are accessible via [http://localhost:4566](http://localhost:4566)
- The Elasticsearch instance is accessible via [http://localhost:9200](http://localhost:9200)
- The Postgres DB is accessible via the username/password/host/port/dbname combo: `masteruser/password/localhost/5432/nasadb`


## Notes

The PDF serialization service supports unicode characters in text mode. The service uses the font `Latin Modern Math` which has a good coverage of unicode math symbols. See a list of symobls here: https://ctan.math.illinois.edu/macros/latex/contrib/unicode-math/unimath-symbols.pdf
A symbol which is not covered by the font will be rendered as a blank space. Unicode characters used in LaTeX math mode will not be rendered.

## Releases

**A new release should be created every time there's a merge to master.**

Releases are tied to a version number and created manually using GH's releases page.
The version in this README should be increased according to [semver](https://semver.org/) and the release tag should follow the format `v<major>.<minor>.<patch>`, ex: `v2.0.1`.
The release description should have a [changelog](https://gist.github.com/vgeorge/e6fd828987b2f7d62a447df2bd132c4a) with "Features", "Improvements" and "Fixes".

# License

This project is licensed under **The MIT License (MIT)**, see the [LICENSE](LICENSE.md) file for more details.
