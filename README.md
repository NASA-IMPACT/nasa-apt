# nasa-apt

## Local development
Code and issues relevant to the NASA APT project

[![CircleCI](https://circleci.com/gh/developmentseed/nasa-apt/tree/master.svg?style=svg)](https://circleci.com/gh/developmentseed/nasa-apt/tree/master)

The project API is built using [Postgrest](https://github.com/PostgREST/postgrest).

To create a test instance of the database and API with `docker-compose` run

`docker-compose build`<br/>

Followed by

`./startserver.sh`<br/>

This will create a test instance of the DB with data loaded, the API and some
stubbed versions of supporting services.

The Swagger API documentation is accessible via [http://localhost:8080](http://localhost:8080).
The API is accessible via [http://localhost:3000](http://localhost:3000).


## Database changes
Database changes and migrations are managed via [sqitch](https://sqitch.org/).
You can find a nice outline of managing Postgres migrations with Sqitch [here](https://sqitch.org/docs/manual/sqitchtutorial/)
This project uses a Sqitch Docker image referencing some local files in order to manage migrations.
As an example, to add a table we could run the following from the project root.

To move to the `db` directory.

`cd db`<br/>

To create a Sqitch `change`

`./sqitch add somechange -n 'Change the database in some way'`<br/>

This creates new empty `sql` scripts in the `deploy`, `revert and `verify` directories.
You can then update the `somechange.sql` script in the `deploy` directory with the necessary change.
See the Sqitch [documentation](https://sqitch.org/docs/manual/sqitchtutorial) for more details on change dependencies and validation.

To update your local environment with the new database changes you need to re-run (note that this will remove any new data stored in your local development database.)

`./startserver.sh`<br/>

## Deploying to AWS
To deploy the AWS infrastructure for the application you will need an
installation of the [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
with credentials which allow creating all the stack resources.

To deploy the AWS infrastructure from the root directory run

`cd cloudformation`<br/>
`./deploy.sh`<br/>

You will be prompted for a stack name and a master db password.  The current
stacks are `nasa-apt-staging` and `nasa-apt-production`.

After the stack has been successfully deployed you can create the database tables.
You will need an installation of the `psql` command line client.  You may also
need to update the RDS instance's security policy to allow inbound traffic from the IP address of the machine where you are executing the deployment.
To create the schema and tables in the AWS RDS from the project root run

`cd db`<br/>
`./sqitch deploy --verify db:pg://{yourmasteruser}:{yourmasterpassword}@{yourRDSendpoint}:5432/nasadb`<br/>

Because of PostgREST's schema reloading [model](http://postgrest.org/en/v5.2/admin.html#schema-reloading) some underlying database changes may require a restart of the PostgREST ECS instances to reflect the changes.

