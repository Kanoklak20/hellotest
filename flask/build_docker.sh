#!/bin/sh
app="docker.test"
docker build -t ${app} .
docker run -p 5000:8000 -d \
  --name=${app} \
  -v $PWD:/flask_app ${app}