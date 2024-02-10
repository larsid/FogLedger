#!/bin/bash

docker build -f ./indy/indy-cli.dockerfile -t indy-cli ./indy
docker build -f ./indy/indy-node.dockerfile -t indy-node ./indy
docker build -f ./indy/webserver.dockerfile -t webserver ./indy
docker build -f ./indy/aca-py.dockerfile -t aca-py ./indy
docker build -f ./indy/httpd.dockerfile -t httpd-fogbed ./indy

docker build -f ./iota/iota.dockerfile -t hornet ./iota
docker build -f ./iota/iota-explorer-api.dockerfile -t iotaledger/explorer-api ./iota
docker build -f ./iota/iota-explorer-web-app.dockerfile -t iotaledger/explorer-webapp ./iota

