FROM postgres:9.4

COPY init.sql /docker-entrypoint-initdb.d/
COPY testData.sql /docker-entrypoint-initdb.d/
