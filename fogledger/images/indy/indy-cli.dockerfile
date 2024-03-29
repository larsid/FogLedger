FROM ubuntu:16.04

RUN apt-get update && apt-get install -y apt-transport-https

ARG indy_stream=master

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial $indy_stream" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y indy-cli \
    net-tools \
    iputils-ping \
    iproute \
    pwgen
RUN echo '{"taaAcceptanceMechanism":"for_session"}' > /cliconfig
RUN indy-cli --config /cliconfig
CMD /bin/bash
