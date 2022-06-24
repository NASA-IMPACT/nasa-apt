FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim as prod
RUN apt-get update \
    && apt-get install -y \
    locales \
    texlive-latex-recommended \
    texlive-bibtex-extra \
    texlive-xetex \
    texlive-science \
    latexmk\
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

WORKDIR /app/

COPY ./README.md /app/README.md
COPY ./app/ /app/app/
COPY ./setup.py /app/setup.py

# Style file for AGU journal pdf
RUN mkdir -p /usr/share/texlive/texmf-dist/tex/latex/agujournal2019/
#RUN chmod 644 ./app/pdf/agujournal2019.cls
COPY ./app/pdf/agujournal2019.cls /usr/share/texlive/texmf-dist/tex/latex/agujournal2019/
# make class file readable to latex compiler
RUN chmod 644 /usr/share/texlive/texmf-dist/tex/latex/agujournal2019/agujournal2019.cls
# register the new .cls file
RUN mktexlsr 

RUN pip install --upgrade pip
RUN pip install . -t .


COPY lambda/handler.py ./handler.py
RUN chmod 644 ./handler.py
RUN chmod -R 755 /app
