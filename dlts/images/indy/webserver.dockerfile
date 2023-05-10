FROM ghcr.io/bcgov/von-network-base:sha-8a6d5e40
USER root
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2
    
     
CMD /bin/bash
