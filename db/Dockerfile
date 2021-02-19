FROM postgres:11.8 as postgres
RUN postgres -c log_statement=all

FROM sqitch/sqitch:latest as sqitch

COPY . .

ENTRYPOINT [ "/bin/sqitch" ] 
CMD ["deploy", "--verify", "db:pg://masteruser:password@host.docker.internal:5432/nasadb"]

