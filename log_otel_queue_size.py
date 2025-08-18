import subprocess
import time
from datetime import datetime

# Configuration parameters
DURATION_MINUTES = 10
INTERVAL_SECONDS = 15
TOTAL_ITERATIONS = (DURATION_MINUTES * 60) // INTERVAL_SECONDS
LOGFILE = 'metrics_log.csv'

# Helper function to run shell commands and get output
def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8')

# Write headers to the log file
with open(LOGFILE, 'w') as log:
    log.write("ElapsedTime,QueueSize,otel-0_CPU,otel-0_MEM,otel2-0_CPU,otel2-0_MEM\n")

# Start time
start_time = time.time()

# Run for the specified number of iterations
for _ in range(TOTAL_ITERATIONS):
    # Get queue size from otel/0 pod using juju ssh
    command = "juju ssh --container otelcol otel/0 curl -s localhost:8888/metrics"
    output = run_command(command)
    queue_size = None
    for line in output.splitlines():
        if 'queue_size{' in line:
            queue_size = line.split()[-1]
            break
    
    # Get CPU and Memory usage for otel-0 and otel2-0
    metrics_output = run_command("sudo k8s kubectl top pod -n otel")
    otel0_cpu, otel0_mem, otel2_cpu, otel2_mem = None, None, None, None
    for line in metrics_output.splitlines():
        if 'otel-0' in line:
            parts = line.split()
            otel0_cpu, otel0_mem = parts[1], parts[2]
        elif 'otel2-0' in line:
            parts = line.split()
            otel2_cpu, otel2_mem = parts[1], parts[2]

    # Get elapsed time and format timestamp
    elapsed = time.time() - start_time
    timestamp = str(datetime.utcfromtimestamp(elapsed).strftime('%M:%S'))

    # Prepare log line
    log_line = f"{timestamp},{queue_size},{otel0_cpu},{otel0_mem},{otel2_cpu},{otel2_mem}"

    # Print to console for debugging
    print(f"DEBUG: {log_line}")

    # Write to log file
    with open(LOGFILE, 'a') as log:
        log.write(log_line + '\n')

    # Wait for the next interval
    time.sleep(INTERVAL_SECONDS)
