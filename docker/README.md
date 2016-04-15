Dockerized Build Agent
======================


### Create docker image
```bash
# cd tc-agent && ./rebuild.sh
```
Note: it will take a while


### Start new builder
```bash
# cd utils/docker
# ./start-docker-container.sh http://109.87.54.17:8112 vk-tc-agent-1
```
where
 `http://109.87.54.17:8112` is TeamCity server url (using http to avoid SSL cert issue)
 `vk-tc-agent-1` - TC agent and Docker container name