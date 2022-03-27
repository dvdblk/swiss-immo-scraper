#!/bin/sh

docker build . -t immo-scraper && docker run --env-file=.env -it immo-scraper