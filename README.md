# nasa-apt

## Local development
Code and issues relevant to the NASA APT project

[![CircleCI](https://circleci.com/gh/developmentseed/nasa-apt/tree/develop.svg?style=svg&circle-token=ffc901ab7ce00ffa5cef07cce59ff64a2c635d2b)](https://circleci.com/gh/developmentseed/nasa-apt/tree/develop)

The project API is built using [Postgrest](https://github.com/PostgREST/postgrest).

To create a test instance of the database and API with `docker-compose` run
```
docker-compose build
```

Followed by
```
./startserver.sh
```
This will take 10-12 seconds for the server instance to spin up before the API is available.

This will create a test instance of the DB with data loaded, the API and some
stubbed versions of supporting services.

The Swagger API documentation is accessible via [http://localhost:8080](http://localhost:8080).
The API is accessible via [http://localhost:3000](http://localhost:3000).


## Database changes
Database changes and migrations are managed via [sqitch](https://sqitch.org/).
You can find a nice outline of managing Postgres migrations with Sqitch [here](https://sqitch.org/docs/manual/sqitchtutorial/)
This project uses a Sqitch Docker image referencing some local files in order to manage migrations.
As an example, to add a table we could run the following from the project root.

To create a Sqitch `change`
```
cd db
./sqitch add somechange --requires previouschange -n 'Change the database in some way'
```

This creates new empty `sql` scripts in the `deploy`, `revert` and `verify` directories.
You can then update the `somechange.sql` script in the `deploy` directory with the necessary change.
See the Sqitch [documentation](https://sqitch.org/docs/manual/sqitchtutorial) for more details on change dependencies and validation.

To update your local environment with the new database changes you need to re-run
```
./startserver.sh
```
(note that this will remove any new data stored in your local development database.)

## Deploying to AWS
To deploy the AWS infrastructure for the application you will need an
installation of the [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
with credentials which allow creating all the stack resources.

To deploy the AWS infrastructure from the root directory run
```
cd cloudformation
./deploy.sh
```

You will be prompted for a stack name and a master db password.  The current
stacks are `nasa-apt-staging` and `nasa-apt-production`.

After the stack has been successfully deployed you can create the database tables.
You will need an installation of the `psql` command line client.  You may also
need to update the RDS instance's security policy to allow inbound traffic from the IP address of the machine where you are executing the deployment.
To create the schema and tables in the AWS RDS from the project root run
```
cd db
./sqitch deploy --verify db:pg://{yourmasteruser}:{yourmasterpassword}@{yourRDSendpoint}:5432/nasadb
```

Because of PostgREST's schema reloading [model](http://postgrest.org/en/v5.2/admin.html#schema-reloading) some underlying database changes may require a restart of the PostgREST ECS instances to reflect the changes.

## Environments
There are currently 2 environments defined for NASA-APT, which follow specific branches
- Staging (`develop`): http://nasa-publi-1l90d8d31sxmx-2113866973.us-east-1.elb.amazonaws.com
- Production (`master`): http://nasa-publi-8fvzs7xeloxf-2015041748.us-east-1.elb.amazonaws.com

**Given that deployment is a manual process it is important that the environments are kept up to date after a merge to `master` or `develop`.**

**NOTE:** Although the product is not yet being fully used, the data in the production environment should not be lost, and should be taken into account on any database migrations.

Steps to deploy:
1 - Make a snapshot backup of the RDS instance.
2 - Update the cloudformation stack if needed (see previous section).
3 - Update the database as described in the previous section. (_The easiest way to get the connection string is to check the env variables of the task of the corresponding ECS cluster_). You may need to add your ip address to the sec group inbound rules.
4 - Force a new deployment of the PostgREST ECS service so that it can infer database schema changes (`aws ecs update-service --force-new-deployment --cluster <cluster> --service <service>`.
