#!/bin/bash

set +x
NUM_CONTAINER=13 #Number for r5.4x instance
LOAD_OFFSET=65
TOOL_SINDEX=1
TOOL_EINDEX=$(expr ${TOOL_SINDEX} + ${LOAD_OFFSET})
#TOOL_EINDEX=${LOAD_OFFSET}
WORKDIR=${PWD}
#WORKDIR=/home/ubuntu/1m7_mqtt_load_gen
ITER_SLEEP_TIME_SEC=$(expr ${LOAD_OFFSET} \* 10 + 300)  #Total time to launch a load in single container
HOST_VOL_PATH=/home/ubuntu
DOCKER_VOL_PATH=/home/ubuntu


for number in $(seq 1 ${NUM_CONTAINER})
do
#echo "Starting docker container: $number ${ITER_SLEEP_TIME_SEC}"
echo "Starting docker container: $number "
echo "Indexes: ${TOOL_SINDEX} ${TOOL_EINDEX}"
#sudo docker run -it --rm -v /home/ubuntu:/home/ubuntu load_tool_image
#time sudo docker run -it --rm -v ${HOST_VOL_PATH}:${DOCKER_VOL_PATH} load_test_vne:0.1
#sudo docker run -d -t --rm -e TOOL_SINDEX=${TOOL_SINDEX} -e TOOL_EINDEX=${TOOL_EINDEX} -w ${WORKDIR} -v ${HOST_VOL_PATH}:${DOCKER_VOL_PATH} load_test_vne:0.1 sleep infinity
time sudo docker run -d -t --rm -e TOOL_SINDEX=${TOOL_SINDEX} -e TOOL_EINDEX=${TOOL_EINDEX} -w ${WORKDIR} -v ${HOST_VOL_PATH}:${DOCKER_VOL_PATH} load_test_vne:0.1
TOOL_SINDEX=$(expr ${TOOL_EINDEX} + 1)
TOOL_EINDEX=$(expr ${TOOL_SINDEX} + ${LOAD_OFFSET})
sleep ${ITER_SLEEP_TIME_SEC}s
done

