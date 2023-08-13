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
    nginx \
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
RUN mv -i explorer/client/.eslintrc.js /app/
RUN mv -i explorer/client/.eslintignore /app/
RUN mv -i explorer/client/.dockerignore /app/
RUN mv -i explorer/client/.env /app/
RUN mv -i explorer/client/.stylelintrc.json /app/
RUN mv -i explorer/client/* /app/


RUN echo 'server {\
    listen       80;\
    server_name  localhost;\
    location / {\
        root   /app/build;\
        index  index.html index.htm;\
        try_files $uri /index.html;\
    }\
  }' > /etc/nginx/sites-available/default

RUN npm install