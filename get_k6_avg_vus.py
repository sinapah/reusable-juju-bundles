import subprocess
import re
import threading
import time

vus_samples = []
queue_sizes = []

otel0_cpus = []
otel0_mems = []
otel2_cpus = []
otel2_mems = []

QUEUE_POLL_INTERVAL = 10 # Running the kubectl top command every 10 seconds
running = True

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True, timeout=10)
    return result.stdout

def poll_queue_size():
    while running:
        command = "juju ssh --container otelcol otel/0 curl -s localhost:8888/metrics"
        output = run_command(command)
        
        queue_size = None
        for line in output.splitlines():
            if 'queue_size{' in line:
                queue_size = line.split()[-1]
                break
        if queue_size is not None:
            
            queue_sizes.append(int(queue_size))
        time.sleep(QUEUE_POLL_INTERVAL)

def get_pod_resources():
    while running:
        metrics_output = run_command("sudo k8s kubectl top pod -n otel")
        otel0_cpu, otel0_mem, otel2_cpu, otel2_mem = None, None, None, None
        for line in metrics_output.splitlines():
            if 'otel-0' in line:
                parts = line.split()
                otel0_cpu, otel0_mem = parts[1], parts[2]
            elif 'otel2-0' in line:
                parts = line.split()
                otel2_cpu, otel2_mem = parts[1], parts[2]
            if otel0_cpu is not None:
                otel0_cpus.append(otel0_cpu)

            if otel0_mem is not None:
                otel0_mems.append(otel0_mem)

            if otel2_cpu is not None:
                otel2_cpus.append(otel2_cpu)

            if otel2_mem is not None:
                otel2_mems.append(otel2_mem)

queue_thread = threading.Thread(target=poll_queue_size)
resources_thread = threading.Thread(target=get_pod_resources)

queue_thread.start()
resources_thread.start()

proc = subprocess.Popen(
    ["/home/ubuntu/repos/opentelemetry-collector-k8s-k6-load-tests/k6", "run", "/home/ubuntu/repos/opentelemetry-collector-k8s-k6-load-tests/scripts/constant-arrival-rate-scenario.js"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True
)

for line in proc.stdout:
    print(line, end='')
    match = re.search(r'(\d+)/\d+ VUs', line)
    if match:
        vus = int(match.group(1))
        
        vus_samples.append(1 if vus == 0 else vus)

running = False
queue_thread.join()

if vus_samples:
    avg_vus = sum(vus_samples) / len(vus_samples)
    print(f"\nAverage VUs: {avg_vus:.2f}")
    print(f"Max number of VUs: {max(vus_samples)}")

if queue_sizes:
    avg_queue = sum(queue_sizes) / len(queue_sizes)
    print(f"Average Queue Size: {avg_queue:.2f}")
    print(f"Max Queue Size: {max(queue_sizes)}")

def parse_cpu(cpu_str):
    # Remove m from string and convert to in
    return float(cpu_str.rstrip('m'))

def parse_mem(mem_str):
    # Converts "512Mi" to 512
    return int(mem_str.rstrip('Mi'))

if otel0_cpus:
    parsed_otel0_cpus = [parse_cpu(cpu) for cpu in otel0_cpus]
    avg_otel0_cpu = sum(parsed_otel0_cpus) / len(parsed_otel0_cpus)
    print(f"Average Otel 0 CPU: {avg_otel0_cpu:.2f} cores")
    print(f"Max Otel 0 CPU: {max(parsed_otel0_cpus):.2f} cores")

if otel0_mems:
    parsed_otel0_mems = [parse_mem(mem) for mem in otel0_mems]
    avg_otel0_mem = sum(parsed_otel0_mems) / len(parsed_otel0_mems)
    print(f"Average Otel 0 MEM: {avg_otel0_mem:.2f} Mi")
    print(f"Max Otel 0 MEM: {max(parsed_otel0_mems)} Mi")

if otel2_cpus:
    parsed_otel2_cpus = [parse_cpu(cpu) for cpu in otel2_cpus]
    avg_otel2_cpu = sum(parsed_otel2_cpus) / len(parsed_otel2_cpus)
    print(f"Average Otel 2 CPU: {avg_otel2_cpu:.2f} cores")
    print(f"Max Otel 2 CPU: {max(parsed_otel2_cpus):.2f} cores")

if otel2_mems:
    parsed_otel2_mems = [parse_mem(mem) for mem in otel2_mems]
    avg_otel2_mem = sum(parsed_otel2_mems) / len(parsed_otel2_mems)
    print(f"Average Otel 2 MEM: {avg_otel2_mem:.2f} Mi")
    print(f"Max Otel 2 MEM: {max(parsed_otel2_mems)} Mi")