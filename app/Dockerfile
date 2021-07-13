FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as prod
RUN apt-get update \
    && apt-get install -y \
    locales \
    texlive-latex-recommended \
    texlive-xetex \
    latexmk\
    wget libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config gcc \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

WORKDIR /app/

COPY ./README.md /app/README.md
COPY ./app/ /app/app/
COPY ./setup.py /app/setup.py


RUN pip install --upgrade pip
RUN pip install . -t .


COPY lambda/handler.py ./handler.py

