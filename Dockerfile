# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /app

ADD app app
COPY etc/urls.json etc/urls.json

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Add environment variables from GitHub actions secrets
RUN --mount=type=secret,id=DISCORD_WEBHOOK \
    --mount=type=secret,id=GOOGLE_MAPS_API_KEY \
    export DISCORD_WEBHOOK=$(cat /run/secrets/DISCORD_WEBHOOK) && \
    export GOOGLE_MAPS_API_KEY=$(cat /run/secrets/GOOGLE_MAPS_API_KEY) && \
    echo "${GOOGLE_MAPS_API_KEY}" | cut -c 6

CMD [ "python3", "-m", "app.main", "-f", "etc/urls.json"]
