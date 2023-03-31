FROM ghcr.io/bcgov/von-network-base:sha-8a6d5e40
USER root
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2 
RUN sed -i "s/host=\"0.0.0.0\"/host=\"localhost\"/g" server/server.py
CMD /bin/bash
