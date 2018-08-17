#!/bin/bash
docker exec -d grapehard$1 /opt/tool_pkg/grapehard/blocking/run_server.py -p
