FROM mcr.microsoft.com/playwright/python:v1.30.0-focal as prod
RUN apt-get update \
    && apt-get install -y \
    locales \
    texlive-latex-recommended \
    texlive-bibtex-extra \
    texlive-xetex \
    texlive-science \
    latexmk \
    libpq-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

WORKDIR /app/

COPY ./README.md /app/README.md
COPY ./app/ /app/app/
COPY ./setup.py /app/setup.py

# Style file for AGU journal pdf
RUN mkdir -p /usr/share/texlive/texmf-dist/tex/latex/agujournal2019/
COPY ./app/pdf/agujournal2019.cls /usr/share/texlive/texmf-dist/tex/latex/agujournal2019/
# make class file readable to latex compiler
RUN chmod 644 /usr/share/texlive/texmf-dist/tex/latex/agujournal2019/agujournal2019.cls
# register the new .cls file
RUN mktexlsr 

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install . -t .

COPY lambda/handler.py ./handler.py
RUN chmod 644 ./handler.py
RUN chmod -R 755 /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
