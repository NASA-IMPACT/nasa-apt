FROM postgrest/postgrest:v7.0.1
USER root
RUN apt-get update \
    && apt-get install -y sqitch \
    libdbd-pg-perl \
    postgresql-client \
    libdbd-sqlite3-perl sqlite3 \
    curl zip jq

RUN curl -o /usr/local/bin/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/$WAITFORIT_VERSION/waitforit-linux_amd64 && \
    chmod +x /usr/local/bin/waitforit

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install


WORKDIR /db