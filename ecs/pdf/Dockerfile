FROM ubuntu

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

COPY base_commands.sh /
RUN ./base_commands.sh