#!/bin/sh

docker build . -t immo-scraper && \
docker run -it --env-file .env immo-scraper
