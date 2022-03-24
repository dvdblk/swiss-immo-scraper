#!/bin/sh

docker build . -t immo-scraper && docker run -it immo-scraper