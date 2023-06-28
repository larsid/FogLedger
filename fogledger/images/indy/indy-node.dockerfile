FROM ubuntu:20.04

ENV NETWORK_NAME=fogbed
RUN apt-get update --allow-insecure-repositories -y && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    gnupg2 \
    ## ToDo remove unused packages
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev \
    libgflags-dev \
    python3-pip \
    net-tools \
    iputils-ping \
    iproute2 \
    pwgen \
    --allow-unauthenticated

# Bionic-security for libssl1.0.0
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3B4FE6ACC0B21F32 \
    && echo "deb http://security.ubuntu.com/ubuntu bionic-security main"  >> /etc/apt/sources.list

# Sovrin
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys CE7709D068DB5E88 \
    && bash -c 'echo "deb https://repo.sovrin.org/deb bionic master" >> /etc/apt/sources.list'

# Hyperledger Artifactory
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 9692C00E657DDE61 \
    && echo "deb https://hyperledger.jfrog.io/artifactory/indy focal rc" >> /etc/apt/sources.list \
    # Prioritize packages from hyperledger.jfrog.io
    && printf '%s\n%s\n%s\n' 'Package: *' 'Pin: origin hyperledger.jfrog.io' 'Pin-Priority: 1001' >> /etc/apt/preferences

RUN pip3 install -U \
    # Required by setup.py
    'setuptools==50.3.2'


RUN apt-get update --allow-insecure-repositories -y && apt-get install -y \
    indy-node="1.13.2~rc5" \
    indy-plenum="1.13.1~rc3" \
    ursa="0.3.2-1" \
    python3-pyzmq="22.3.0" \
    rocksdb="5.8.8" \
    python3-importlib-metadata="3.10.1" --allow-unauthenticated\
    && rm -rf /var/lib/apt/lists/* \
    # fix path to libursa
    && ln -s /usr/lib/ursa/libursa.so /usr/lib/libursa.so
RUN awk -v var="${NETWORK_NAME}" '{if (index($1, "NETWORK_NAME") != 0) {print("NETWORK_NAME = \"" var "\"")} else print($0)}' /etc/indy/indy_config.py> /tmp/indy_config.py
RUN mv /tmp/indy_config.py /etc/indy/indy_config.py
RUN mkdir /var/lib/indy/${NETWORK_NAME}
RUN mkdir /tmp/indy/

COPY scripts /opt/indy/scripts/
RUN chmod +x /opt/indy/scripts/change_mtu.bash
CMD ["bash"]

