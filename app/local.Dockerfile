FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as prod
RUN apt-get update \
    && apt-get install -y \
    locales \
    texlive-latex-recommended \
    texlive-xetex \
    wget libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config gcc \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8
# install python packages (note fastapi and uvicorn should already by satisfied from the prod target)

WORKDIR /app/

COPY ./README.md /app/README.md
COPY ./app/ /app/app/
COPY ./setup.py /app/setup.py


RUN pip install --upgrade pip
RUN pip install /app/. "mangum>=0.9.0" -t . --no-binary xmlsec numpy pydantic


#FROM prod as dev
#CMD ["/start-reload.sh"]


