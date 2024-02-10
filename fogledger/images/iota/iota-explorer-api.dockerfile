FROM ubuntu:20.04

USER root

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get install -y \
    bash \
    net-tools \
    iputils-ping \
    iproute2 \
    pwgen \
    jq \
    git \
    curl \
    python3 \
    build-essential \
    cmake && \
    rm -rf /var/lib/apt/lists/*

# Baixe e instale o Node.js v16.16.0
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Atualize o npm para a versão 8.8.0
RUN npm install -g npm@8.8.0

# Working DIR
WORKDIR /app

RUN git clone --depth 1 --branch dev https://github.com/iotaledger/explorer.git explorer
RUN mv explorer/api/* /app/
RUN mv -i explorer/api/.eslintrc.js /app/
RUN mv -i explorer/api/.eslintignore /app/
RUN mv -i explorer/api/.dockerignore /app/

# Set the env variables
ARG CONFIG_ID