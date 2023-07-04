FROM ubuntu:20.04

COPY --chown=root:root --from=iotaledger/hornet /app /app

WORKDIR /app

USER root

RUN apt-get update && apt-get install -y \
    bash \
    net-tools \
    iputils-ping \
    iproute2 \
    pwgen \
    jq