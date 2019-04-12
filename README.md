# nasa-apt
Code and issues relevant to the NASA APT project

The project API is built using [Postgrest](https://github.com/PostgREST/postgrest).

To create a test instance of the database and API with `docker-compose` run

`docker-compose build` 

Followed by

`./startserver.sh`

This will create a test instance of the DB with data loaded, the API and some
stubbed versions of supporting services.

The Swagger API documentation is accessible via [http://localhost:8080](http://localhost:8080).
The API is accessible via [http://localhost:3000](http://localhost:3000).
