#!/bin/bash

docker build -f ./indy/indy-cli.dockerfile -t indy-cli ./indy
docker build -f ./indy/indy-node.dockerfile -t indy-node ./indy
