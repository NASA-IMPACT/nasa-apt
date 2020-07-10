# PDF Serialization Service

Serialization worker for db -> json -> latex -> pdf. Uses multistage docker build for prod, dev environments.

## production stage 

The base image has python, fastapi, and the app dependencies. To prevent the dev stage from building, remember to
target the `prod` stage only with a build target, e.g.

```shell script
docker build --target prod . -t nasa-apt/prod/pdf
docker run \
    --env AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --env AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    --env API_PREFIX=/pdf/ \
    --env FIGURES_S3_BUCKET=$FIGURES_S3_BUCKET \
    --env PDFS_S3_BUCKET=$PDFS_S3_BUCKET \
    --env REST_API_ENDPOINT=$REST_API_ENDPOINT \
    --env S3_ENDPOINT=$S3_ENDPOINT \
    -d \
    -p 80:80 \
    nasa-apt/prod/pdf
```

## development stage

The `startserver.sh` script uses `docker-compose.yml` and sets all the environment variables and a bind mount
for live reloading of python scripts. If you wanted to run the container manually, it would be like this:

```shell script
# dev is the default build stage
docker build . -t nasa-apt/dev/pdf
docker run \
    --env AWS_ACCESS_KEY_ID=stub \
    --env AWS_SECRET_ACCESS_KEY=stub \
    --env FIGURES_S3_BUCKET=$FIGURES_S3_BUCKET \
    --env PDFS_S3_BUCKET=$PDFS_S3_BUCKET \
    --env REST_API_ENDPOINT=$REST_API_ENDPOINT \
    --env S3_ENDPOINT=$S3_ENDPOINT \
    -it \
    --mount type=bind,source="$(pwd)"/app,target=/app \ 
    -p 8000:8000 \
    nasa-apt/dev/pdf
```

