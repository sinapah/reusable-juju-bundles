#!/bin/bash

# Simulate some values
RANDOM_VALUE=$((RANDOM % 100))
CURRENT_TIME=$(date +%s)

cat <<EOF
# HELP example_random_value Random number between 0 and 99
# TYPE example_random_value gauge
example_random_value ${RANDOM_VALUE}

# HELP example_last_run_timestamp Unix timestamp of last execution
# TYPE example_last_run_timestamp gauge
example_last_run_timestamp ${CURRENT_TIME}
EOF
