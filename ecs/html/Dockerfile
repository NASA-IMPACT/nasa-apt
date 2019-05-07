FROM arxivvanity/engrafo

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apt-get update
RUN apt-get install -y awscli

WORKDIR /app