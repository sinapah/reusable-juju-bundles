import subprocess
import time
from datetime import datetime

# Configuration parameters
DURATION_MINUTES = 10
INTERVAL_SECONDS = 15
TOTAL_ITERATIONS = (DURATION_MINUTES * 60) // INTERVAL_SECONDS
LOGFILE = 'ten_vus.csv'

# Helper function to run shell commands and get output
def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8')

# Write headers to the log file
with open(LOGFILE, 'w') as log:
    log.write("Elapsed Time,Otel Queue Size,Otel CPU,Otel Memory,Loki-Standin CPU,Loki-Standin Memory,Otel Sent Logs,Total Number of Incoming Items For Otel,Total Number of Outgoing Items For Otel,Number of Logs Accepted By Loki Stand-In,Number of Logs Refused By Loki Stand-In\n")

# Start time
start_time = time.time()

# Run for the specified number of iterations
for _ in range(TOTAL_ITERATIONS):
    # Get queue size from Otel (the otel under load testing) pod using juju ssh
    command = "juju ssh --container otelcol otel/0 curl -s localhost:8888/metrics"
    output = run_command(command)
    queue_size = None
    for line in output.splitlines():
        if 'queue_size{' in line:
            queue_size = line.split()[-1]
            break
    
    # This step is to curl the metrics endpoint for Otel (the otel under load testing) and get the number of sent logs
    command = "juju ssh --container otelcol otel/0 curl -s localhost:8888/metrics"
    output = run_command(command)
    otel_sent_logs = None
    for line in output.splitlines():
        if 'otelcol_exporter_sent_log_records{' in line:
            otel_sent_logs = line.split()[-1]
            break
    
    # This step is to curl the metrics endpoint for Otel (the otel under load testing) and get the total number of incoming items
    command = "juju ssh --container otelcol otel/0 curl -s localhost:8888/metrics"
    output = run_command(command)
    otel_incoming_items = None
    for line in output.splitlines():
        if 'otelcol_processor_incoming_items{' in line:
            otel_incoming_items = line.split()[-1]
            break

    # This step is to curl the metrics endpoint for Otel (the otel under load testing) and get the total number of outgoing items
    command = "juju ssh --container otelcol otel/0 curl -s localhost:8888/metrics"
    output = run_command(command)
    otel_outgoing_items = None
    for line in output.splitlines():
        if 'otelcol_processor_outgoing_items{' in line:
            otel_outgoing_items = line.split()[-1]
            break
    
    # This step is to curl the metrics endpoint for Otel 2 (the Loki stand-in) and get the number of log records that could not be pushed into the pipeline
    command = "juju ssh --container otelcol otel2/0 curl -s localhost:8888/metrics"
    output = run_command(command)
    loki_refused_logs = None
    for line in output.splitlines():
        if 'otelcol_receiver_refused_log_records{' in line:
            loki_refused_logs = line.split()[-1]
            break
    
    # This step is to curl the metrics endpoint for Otel 2 (the Loki stand-in) and get the number of accepted logs records
    command = "juju ssh --container otelcol otel/0 curl -s localhost:8888/metrics"
    output = run_command(command)
    loki_accepted_logs = None
    for line in output.splitlines():
        if 'otelcol_receiver_accepted_log_records{' in line:
            loki_accepted_logs = line.split()[-1]
            break
    
    # Get CPU and Memory usage for otel-0 and otel2-0
    metrics_output = run_command("sudo k8s kubectl top pod -n otel2")
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
    log_line = f"{timestamp},{queue_size},{otel0_cpu},{otel0_mem},{otel2_cpu},{otel2_mem},{otel_sent_logs},{otel_incoming_items},{otel_outgoing_items},{loki_accepted_logs},{loki_refused_logs}"

    # Print to console for debugging
    print(f"DEBUG: {log_line}")

    # Write to log file
    with open(LOGFILE, 'a') as log:
        log.write(log_line + '\n')

    # Wait for the next interval
    time.sleep(INTERVAL_SECONDS)
