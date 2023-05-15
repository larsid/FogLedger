FROM ubuntu:focal
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2 \
    python3 \
    wget \
    pwgen \
    apache2
    
CMD /bin/bash