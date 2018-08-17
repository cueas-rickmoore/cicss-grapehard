#!/bin/bash
docker run -dit --name grapehard$2 -v /home/web/nrcc_data/cicca:/app_data:ro -p 20007:20007 cicca/grapehard:$1
sleep 10s
docker exec -d grapehard$2 /opt/tool_pkg/grapehard/blocking/run_server.py -p
