FROM ubuntu:xenial as indy-baseimage
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"
ENV NETWORK_NAME=fogbed
RUN apt-get update && apt-get dist-upgrade -y

# very common packages
RUN apt-get update && apt-get install -y \
    git \
    wget \
    vim \
    apt-transport-https \
    ca-certificates \
    apt-utils 
    
RUN apt install -y \
    net-tools \
    iputils-ping \
    iproute
# python
RUN apt-get update && apt-get install -y \
    python3.5 \
    python3-pip \
    python-setuptools
    
# pypi based packages
RUN pip3 install -U\
    "pip <10.0.0" \
    "setuptools<=50.3.2"

# needs to be installed separately and pinned to version 20.0.25 to be compatible with Python3.5 and packages like zipp==1.2.0
RUN pip3 install -U \
    'virtualenv==20.0.35'


RUN ln -s /usr/bin/pip3 /usr/bin/pip

COPY scripts/clean.sh /usr/local/bin/indy_image_clean
RUN chmod 755 /usr/local/bin/indy_image_clean


RUN indy_image_clean

CMD /bin/bash


FROM indy-baseimage as indy-baseci
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

# indy repos
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 && \
    echo "deb https://repo.sovrin.org/deb xenial master" >> /etc/apt/sources.list && \
    apt-get update

COPY scripts/user.sh /usr/local/bin/indy_ci_add_user
RUN bash -c "chmod 755 /usr/local/bin/indy_ci_add_user"


RUN indy_image_clean

FROM indy-baseci
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

# indy repos
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial master" >> /etc/apt/sources.list && \
    apt-get update

# set highest priority for indy sdk packages in core repo
COPY indy-core-repo.preferences /etc/apt/preferences.d/indy-core-repo


RUN indy_image_clean
ARG uid=1000
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 || \
	apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys CE7709D068DB5E88
ARG indy_stream=master
RUN echo "deb https://repo.sovrin.org/deb xenial $indy_stream" >> /etc/apt/sources.list

RUN useradd -ms /bin/bash -u $uid indy

ARG indy_plenum_ver=1.12.1~dev989
ARG indy_node_ver=1.12.1~dev1172
ARG python3_indy_crypto_ver=0.4.5
ARG indy_crypto_ver=0.4.5
ARG python3_pyzmq_ver=18.1.0
ARG python3_orderedset_ver=2.0
ARG python3_psutil_ver=5.4.3
ARG python3_pympler_ver=0.5

RUN apt-get update -y && apt-get install -y \
        python3-pyzmq=${python3_pyzmq_ver} \
        indy-plenum=${indy_plenum_ver} \
        indy-node=${indy_node_ver} \
        python3-indy-crypto=${python3_indy_crypto_ver} \
        libindy-crypto=${indy_crypto_ver} \
        python3-orderedset=${python3_orderedset_ver} \
        python3-psutil=${python3_psutil_ver} \
        python3-pympler=${python3_pympler_ver} \
        vim
RUN awk -v var="${NETWORK_NAME}" '{if (index($1, "NETWORK_NAME") != 0) {print("NETWORK_NAME = \"" var "\"")} else print($0)}' /etc/indy/indy_config.py> /tmp/indy_config.py
RUN mv /tmp/indy_config.py /etc/indy/indy_config.py
RUN mkdir /var/lib/indy/${NETWORK_NAME}