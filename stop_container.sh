#!/bin/bash
echo "List of running containers: "
sudo docker container ls -a
echo "Stopping them..."
sudo docker container ls -a | awk {'print $1'} | xargs sudo docker container stop
sudo docker container ls -a | awk {'print $1'} | xargs sudo docker container rm

