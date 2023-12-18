FROM postgres:latest

COPY init.sql ./tools/init.sql:/docker-entrypoint-initdb.d/

EXPOSE 5432