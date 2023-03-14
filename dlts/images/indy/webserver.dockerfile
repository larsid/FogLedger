FROM ghcr.io/bcgov/von-network-base:sha-211d1817
USER root
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2 
CMD /bin/bash