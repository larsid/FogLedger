FROM ghcr.io/bcgov/von-network-base:sha-211d1817
USER root
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2 
RUN sed -i "s/host='0\.0\.0\.0'/host='localhost'/g" server/server.py
CMD /bin/bash