FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

ENV NETWORK_NAME=fogbed

RUN apt-get update -y && apt-get install -y \
    ca-certificates \
    gnupg2

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88

RUN bash -c 'echo "deb https://repo.sovrin.org/deb xenial stable" >> /etc/apt/sources.list'
RUN apt-get update -y && apt-get install -y python3-pip \
    net-tools \
    iputils-ping \
    iproute2 \
    indy-node
    
RUN awk -v var="${NETWORK_NAME}" '{if (index($1, "NETWORK_NAME") != 0) {print("NETWORK_NAME = \"" var "\"")} else print($0)}' /etc/indy/indy_config.py> /tmp/indy_config.py
RUN mv /tmp/indy_config.py /etc/indy/indy_config.py
RUN mkdir /var/lib/indy/${NETWORK_NAME}
RUN mkdir /tmp/indy/

RUN chown -R indy:indy /var/lib/indy/${NETWORK_NAME}
RUN chown -R indy:indy /tmp/indy/

COPY scripts /opt/indy/scripts/
CMD ["bash"]

EXPOSE 9701 9702 9703 9704 9705 9706 9707 9708 9709 9710
