FROM mcr.microsoft.com/playwright/python:v1.30.0-focal as prod
RUN apt-get update \
    && apt-get install -y \
    locales \
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

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install . -t .

COPY lambda/handler.py ./handler.py
RUN chmod 644 ./handler.py
RUN chmod -R 755 /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
