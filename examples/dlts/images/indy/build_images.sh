#!/bin/bash

docker build -f indy-cli.dockerfile -t indy-cli .
docker build -f indy-node.dockerfile -t indy-node .
