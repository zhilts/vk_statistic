FROM ubuntu

RUN apt-get update
RUN apt-get install -y wget unzip git python-setuptools gcc python-dev
RUN easy_install Fabric3

# SSH KEYGEN
RUN ssh-keygen -b 1024 -C "teamcity agent" -t rsa -f ~/.ssh/id_rsa -N ''
ADD ./ssh-config ~/.ssh/config

# JAVA
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list \
    && echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 \
    && apt-get update \
    && echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections \
    && apt-get install -y oracle-java8-installer oracle-java8-set-default


# TC AGENT
ADD ./agent-setup.sh /
RUN START_CONF=/etc/init/tc-agent-start.conf \
    && echo "start on startup" | tee $START_CONF \
    && echo "task" | tee -a $START_CONF \
    && echo "exec /agent-setup.sh" | tee -a $START_CONF
