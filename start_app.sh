#!/bin/bash
for number in {1..1}
do
echo "Starting batch : $number "
python2.7 main.py $number &
sleep 10s
done
exit 0

echo "App started"
