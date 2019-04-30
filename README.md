# nasa-apt
Code and issues relevant to the NASA APT project

[![CircleCI](https://circleci.com/gh/developmentseed/nasa-apt/tree/master.svg?style=svg)](https://circleci.com/gh/developmentseed/nasa-apt/tree/master)

The project API is built using [Postgrest](https://github.com/PostgREST/postgrest).

To create a test instance of the database and API with `docker-compose` run

`docker-compose build` 

Followed by

`./startserver.sh`

This will create a test instance of the DB with data loaded, the API and some
stubbed versions of supporting services.

The Swagger API documentation is accessible via [http://localhost:8080](http://localhost:8080).
The API is accessible via [http://localhost:3000](http://localhost:3000).

If you make changes to the database table structure defined in `init.sql` you
will need to remove and rebuild the database docker image with the following commands.

`docker-compose stop`
`docker-compose rm`
`docker rmi nasa_apt_db`
`./startserver.sh`

To deploy the AWS infrastructure for the application you will need an
installation of the [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
with credentials which allow creating all the stack resources.

To deploy the AWS infrastructure from the root directory run

`cd cloudformation`
`./deploy.sh`

After the stack has been successfully deployed you can create the database
schema and tables.  You will need an installation of the `psql` command line
client.  To create the schema and tables in the AWS RDS run  

`./createschema.sh`
 
 To deploy the front end application to AWS using the stack resources you just
 created from the root directory run

`cd app`
`./deploy.sh`

