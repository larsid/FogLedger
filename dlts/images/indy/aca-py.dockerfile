FROM bcgovimages/aries-cloudagent:py36-1.16-1_0.7.3
USER root
RUN apt-get update && apt-get install -y net-tools \
    iputils-ping \
    iproute2 
CMD /bin/bash