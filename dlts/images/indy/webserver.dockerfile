FROM ghcr.io/bcgov/von-network-base:latest
USER root
RUN apt-get update && apt-get install -y indy-cli \
    net-tools \
    iputils-ping \
    iproute \
    pwgen
CMD /bin/bash