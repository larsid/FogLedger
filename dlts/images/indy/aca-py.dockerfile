FROM ubuntu:focal
USER root
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2 \
    python3-pip
RUN pip install aries-cloudagent
CMD /bin/bash