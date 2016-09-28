#!/usr/bin/env bash

AGENT_DIR="${HOME}/agent"

if [ -z "$TEAMCITY_SERVER" ]; then
    echo "Fatal error: TEAMCITY_SERVER is not set."
    echo "Launch this container with -e TEAMCITY_SERVER=http://servername:port."
    echo
    exit
fi

if [ ! -d "$AGENT_DIR" ]; then
    cd ${HOME}
    echo "Setting up TeamCityagent for the first time..."
    echo "Agent will be installed to $AGENT_DIR."
    mkdir -p ${AGENT_DIR}
    wget ${TEAMCITY_SERVER}/update/buildAgent.zip
    unzip -q -d ${AGENT_DIR} buildAgent.zip
    rm buildAgent.zip
    chmod +x ${AGENT_DIR}/bin/agent.sh
    echo "serverUrl=${TEAMCITY_SERVER}" > ${AGENT_DIR}/conf/buildAgent.properties
    echo "name=${TEAMCITY_AGENTNAME}" >> ${AGENT_DIR}/conf/buildAgent.properties
    echo "workDir=../work" >> ${AGENT_DIR}/conf/buildAgent.properties
    echo "tempDir=../temp" >> ${AGENT_DIR}/conf/buildAgent.properties
    echo "systemDir=../system" >> ${AGENT_DIR}/conf/buildAgent.properties
else
    echo "Using agent at ${AGENT_DIR}."
fi

service postgresql start

git config --global user.email "$TEAMCITY_AGENTNAME@$TEAMCITY_SERVER"
git config --global user.name "$TEAMCITY_AGENTNAME"
git config --global push.default simple

${AGENT_DIR}/bin/agent.sh start

echo "public ssh key:"
cat ~/.ssh/id_rsa.pub