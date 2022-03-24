# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /app

ADD etc etc
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m", "app.main", "-f", "etc/urls.json"]
