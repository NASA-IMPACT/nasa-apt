FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as prod
RUN apt-get update \
    && apt-get install -y \
    locales \
    texlive-latex-recommended \
    texlive-bibtex-extra \
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

# Style file for AGU journal pdf
RUN mkdir -p /usr/share/texlive/texmf-dist/tex/xetex/agu/
COPY ./app/pdf/agujournal2019.cls /usr/share/texlive/texmf-dist/tex/xetex/agu/agujournal2019.cls

RUN pip install --upgrade pip
RUN pip install . -t .


COPY lambda/handler.py ./handler.py

