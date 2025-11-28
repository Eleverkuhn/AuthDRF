FROM python:3.13.7-slim

RUN apt-get update && apt-get install -y curl tar && rm -rf /var/lib/apt/lists/*

ENV DOCKERIZE_VERSION v0.6.1
RUN curl -L https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz \
    | tar -C /usr/local/bin -xz

RUN dockerize --version

WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install .
EXPOSE 8000
