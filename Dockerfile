# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /app

ADD app app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD [ "python3", "-m", "app.main", "-f", "etc/urls.json"]
