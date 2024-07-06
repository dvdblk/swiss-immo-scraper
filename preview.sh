#!/bin/sh

docker build . -t immo-scraper-preview -f Dockerfile.preview && \
docker run -it --env-file .env immo-scraper-preview