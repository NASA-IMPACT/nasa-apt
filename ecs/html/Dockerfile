FROM arxivvanity/engrafo

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apt-get update
RUN apt-get install python3-pip --assume-yes
RUN pip3 install awscli

WORKDIR /app