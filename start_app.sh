#!/bin/bash
for number in {11..20}
do
echo "Starting batch : $number "
python2.7 main.py v3 $number &
sleep 10s
done
exit 0

echo "App started"
