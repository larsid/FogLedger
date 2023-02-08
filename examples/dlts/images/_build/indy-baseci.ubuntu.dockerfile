FROM hyperledger/indy-baseimage:0.0.4
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

# indy repos
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 && \
    echo "deb https://repo.sovrin.org/deb xenial master" >> /etc/apt/sources.list && \
    apt-get update

COPY scripts/user.sh /usr/local/bin/indy_ci_add_user
RUN bash -c "chmod 755 /usr/local/bin/indy_ci_add_user"

COPY _build/indy-baseci.version /

RUN indy_image_clean
