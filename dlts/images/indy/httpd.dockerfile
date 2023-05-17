FROM httpd:2.4.57-bullseye
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2 \
    python3 \
    wget \
    pwgen \
    apache2
COPY scripts /opt/indy/scripts/
RUN chmod +x /opt/indy/scripts/change_mtu.bash
CMD /bin/bash