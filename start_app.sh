#!/bin/bash
if [[ -z "${TOOL_SINDEX}" ]]; then
  echo "TOOL_SINDEX not defined"
  exit 0
fi
if [[ -z "${TOOL_EINDEX}" ]]; then
  echo "TOOL_EINDEX not defined"
  exit 0
fi
if [[ -z "${TOOL_CONFIG}" ]]; then
  echo "TOOL_CONFIG not defined"
  exit 0
fi

echo "batch range: $TOOL_SINDEX $TOOL_EINDEX"
for number in $(seq $TOOL_SINDEX $TOOL_EINDEX)
do
echo "Starting batch : $number "
python2.7 main.py v3 $number ${TOOL_CONFIG} &
sleep 10s
done
echo "App started"

#tail -f start_app.sh
