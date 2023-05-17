#!/bin/bash

docker build -f ./indy/indy-cli.dockerfile -t indy-cli ./indy
docker build -f ./indy/indy-node.dockerfile -t indy-node ./indy
docker build -f ./indy/webserver.dockerfile -t webserver ./indy
docker build -f ./indy/aca-py.dockerfile -t aca-py ./indy
docker build -f ./indy/httpd.dockerfile -t httpd-fogbed ./indy

