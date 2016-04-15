FROM ubuntu

RUN apt-get install -y wget

RUN wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh


# TC AGENT
ADD ./agent-setup.sh /
#RUN chmod +x /root/files/agent-setup.sh
RUN START_CONF=/etc/init/tc-agent-start.conf \
    && echo "start on startup" | tee $START_CONF \
    && echo "task" | tee -a $START_CONF \
    && echo "exec /agent-setup.sh" | tee -a $START_CONF

#ADD ./agent-start.sh /root/