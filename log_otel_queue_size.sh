#!/bin/bash

LOGFILE="queue_size_log.txt"
DURATION_MINUTES=10
INTERVAL_SECONDS=15
TOTAL_ITERATIONS=$(( (DURATION_MINUTES * 60) / INTERVAL_SECONDS ))
START_TIME=$(date +%s)

echo "ElapsedTime,QueueSize" > "$LOGFILE"

for (( i=1; i<=TOTAL_ITERATIONS; i++ ))
do
    OUTPUT=$(juju ssh --container otelcol otel/0 curl localhost:8888/metrics | grep 'queue_size{')
    VALUE=$(echo "$OUTPUT" | awk '{print $NF}')
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))
    MINUTES=$((ELAPSED / 60))
    SECONDS=$((ELAPSED % 60))
    TIMESTAMP=$(printf "%02d:%02d" $MINUTES $SECONDS)
    echo "$TIMESTAMP,$VALUE" >> "$LOGFILE"
    sleep $INTERVAL_SECONDS
done

