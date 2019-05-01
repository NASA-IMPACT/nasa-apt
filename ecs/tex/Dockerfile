FROM texbase

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

WORKDIR /app
COPY serialize.py /app
COPY ATBD.tex /app