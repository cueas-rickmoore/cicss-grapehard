#!/bin/bash
docker build -t cicca/grapehard:$1 -f ./DockerFiles/Dockerfile_$1.grapehard .
