# nasa-apt

**Version:** 0.3.0

## Local development
Code and issues relevant to the NASA APT project

[![CircleCI](https://circleci.com/gh/developmentseed/nasa-apt/tree/develop.svg?style=svg&circle-token=ffc901ab7ce00ffa5cef07cce59ff64a2c635d2b)](https://circleci.com/gh/developmentseed/nasa-apt/tree/develop)

The project API is built using [Postgrest](https://github.com/PostgREST/postgrest).

The startserver script uses `docker-compose` to build and run the development environment and
sample database: 

```shell script
./startserver.sh
```

This will create a complete development environment with an instance of the DB, the REST API, `localstack` for s3, and
the PDF serialization service.

- The Swagger API documentation is accessible via [http://localhost:8080](http://localhost:8080).
- The REST API is accessible via [http://localhost:3000](http://localhost:3000).

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

To update your local environment with the new database changes you need to re-run
```shell script
./startserver.sh
```
(note that this will remove any new data stored in your local development database.)

## Deploying to AWS

To deploy the AWS infrastructure for the application you will need an
installation of the [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
with credentials which allow creating all the stack resources.

To deploy the AWS infrastructure from the root directory run
```shell script
cd cloudformation
./deploy.sh
```

You will be prompted for a stack name and a master db password.  The current
stacks are `nasa-aptv2-staging` and `nasa-aptv2-production`.

After the stack has been successfully deployed you can create the database tables.
You will need an installation of the `psql` command line client.  

You will also need to update the RDS instance's security policy to allow inbound traffic from the IP address of the machine where you 
are executing the deployment. (see Resources | DBInstance | Security and Network | Security Groups |
Edit inbound rules | Custom TCP, Port 5432, My IP). 

To create the schema and tables in the AWS RDS from the project root run
```shell script
cd db
./sqitch deploy --verify db:pg://{yourmasteruser}:{yourmasterpassword}@{yourRDSendpoint}:5432/nasadb
```

Because of PostgREST's schema reloading [model](http://postgrest.org/en/v5.2/admin.html#schema-reloading) some 
underlying database changes may require a forced redeployment of the PostgREST ECS service to reflect the changes. (See Note in 
[Environments](#environments))

## Environments
There are currently 2 environments defined for NASA-APT, which follow specific branches
- Staging (`develop`): http://nasa-Publi-1UDVJHRLIQD2G-1353740340.us-east-1.elb.amazonaws.com
- Production (`master`): http://nasa-Publi-1LGW8ZYHL7SF7-1834206210.us-east-1.elb.amazonaws.com

**Given that deployment is a manual process it is important that the environments are kept up to date after a merge to `master` or `develop`.**

**NOTE:** Although the product is not yet being fully used, the data in the production environment should not be lost, and should be taken into account on any database migrations.

Steps to deploy:
1. Make a snapshot backup of the RDS instance.
2. Update the cloudformation stack if needed (see previous section).
3. Update the database as described in the previous section. (_The easiest way to get the connection string is to check the env variables of the task of the corresponding ECS cluster_). You may need to add your ip address to the sec group inbound rules.
4. Force a new deployment of the PostgREST ECS service so that it can infer database schema changes:

```shell script
aws ecs update-service --force-new-deployment --cluster <cluster-id> --service <service-arn>
# e.g. 
aws ecs update-service --force-new-deployment --cluster stackname-ECSCluster-nWSsDVGj9NXS --service stackname-svc-pgr 
# then wait until the service's desired count == the running count (this will take about 10 minutes)
```

## Updating the PDF service
The PDF generation service uses docker and it is stored on amazon ECR. During the first cloudformation deployment, the container is created and uploaded, but subsequent updates need to be performed manually.  
We're currently using a single ECR repo (nasa-apt/prod/pdf) to store the container and it is shared between the production and staging environments.

1) Build the container
```
cd nasa-apt/pdf/
# from the pdf/Readme
docker build --target prod . -t nasa-apt/prod/pdf
```
2) Go to the [ECR page](https://us-east-1.console.aws.amazon.com/ecr/repositories?region=us-east-1), select the correct repo and click "View Push Commands".
3) Follow steps 1, 3, and 4.
4) Update the pdf service. Easiest way to know the cluster and service is to go to the [ECS cluster](https://us-east-1.console.aws.amazon.com/ecs/home?region=us-east-1#/clusters)page and selecting the appropriate one.
```
aws ecs update-service --force-new-deployment --cluster <cluster> --service <service>
```

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
