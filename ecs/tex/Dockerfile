FROM python:3

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

COPY requirements.txt /

COPY base_commands.sh /
RUN ./base_commands.sh

WORKDIR /app