#!/bin/bash

if [ $# -ne 1 ]
then
    version=`python3 -c 'import sprp; print(sprp.__version__)'`
else
    version=$1
fi

echo Build image: sprp-web version: ${version}
docker build -t sprp-web -f Dockerfile-sprp .

echo Upload sololxy/sprp-web:${version} ...
docker tag sprp-web sololxy/sprp-web:${version}
docker push sololxy/sprp-web:${version}

echo Upload sololxy/sprp-web:latest
docker tag sprp-web sololxy/sprp-web
docker push sololxy/sprp-web