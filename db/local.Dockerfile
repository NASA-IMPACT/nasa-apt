FROM postgrest/postgrest:latest
USER root
RUN apt-get update \
    && apt-get install -y sqitch libdbd-pg-perl postgresql-client libdbd-sqlite3-perl sqlite3 

WORKDIR /sqitch
