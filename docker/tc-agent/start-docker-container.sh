#!/usr/bin/env bash

if [ "$1" ]; then
    TEAMCITY_SERVER=$1
else
    echo "Where is your TeamCity server?"
    read TEAMCITY_SERVER
fi

if [ "$2" ]; then
    AGENT_NAME=$2
else
    echo "Put name for new docker-container/teamcity-builder"
    read AGENT_NAME
fi

docker run -e TEAMCITY_SERVER=$TEAMCITY_SERVER -e TEAMCITY_AGENTNAME=$AGENT_NAME -dt --name $AGENT_NAME vk/agent
docker exec $AGENT_NAME /root/files/agent-setup.sh