import subprocess
import re
import threading
import time
import sys

vus_samples = []
queue_sizes = []

otel0_cpus = []
otel0_mems = []
otel2_cpus = []
otel2_mems = []
loki0_cpus = []
loki0_mems = []
loki1_cpus = []
loki1_mems = []
loki2_cpus = []
loki2_mems = []

QUEUE_POLL_INTERVAL = 10
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
        loki0_cpu, loki0_mem, loki1_cpu, loki1_mem, loki2_cpu, loki2_mem = None, None, None, None, None, None
        for line in metrics_output.splitlines():
            if 'otel-0' in line:
                parts = line.split()
                otel0_cpu, otel0_mem = parts[1], parts[2]
            elif 'otel2-0' in line:
                parts = line.split()
                otel2_cpu, otel2_mem = parts[1], parts[2]
            elif 'loki-0' in line:
                parts = line.split()
                loki0_cpu, loki0_mem = parts[1], parts[2]
            elif 'loki-1' in line:
                parts = line.split()
                loki1_cpu, loki1_mem = parts[1], parts[2]
            elif 'loki-2' in line:
                parts = line.split()
                loki2_cpu, loki2_mem = parts[1], parts[2]

        if otel0_cpu is not None:
            otel0_cpus.append(otel0_cpu)

        if otel0_mem is not None:
            otel0_mems.append(otel0_mem)

        if otel2_cpu is not None:
            otel2_cpus.append(otel2_cpu)

        if otel2_mem is not None:
            otel2_mems.append(otel2_mem)

        if loki0_cpu is not None:
            loki0_cpus.append(loki0_cpu)
        
        if loki0_mem is not None:
            loki0_mems.append(loki0_mem)
        
        if loki1_cpu is not None:
            loki1_cpus.append(loki1_cpu)
        
        if loki1_mem is not None:
            loki1_mems.append(loki1_mem)
        
        if loki2_cpu is not None:
            loki2_cpus.append(loki2_cpu)
        
        if loki2_mem is not None:
            loki2_mems.append(loki2_mem)

if len(sys.argv) != 3:
    print("Usage: python3 script.py <path_to_k6_binary> <path_to_k6_script>")
    sys.exit(1)

k6_binary = sys.argv[1]
k6_script = sys.argv[2]

queue_thread = threading.Thread(target=poll_queue_size)
resources_thread = threading.Thread(target=get_pod_resources)

queue_thread.start()
resources_thread.start()

proc = subprocess.Popen(
    [k6_binary, "run", k6_script],
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
    return float(cpu_str.rstrip('m'))

def parse_mem(mem_str):
    return int(mem_str.rstrip('Mi'))

if otel0_cpus:
    parsed_otel0_cpus = [parse_cpu(cpu) for cpu in otel0_cpus]
    avg_otel0_cpu = sum(parsed_otel0_cpus) / len(parsed_otel0_cpus)
    print(f"Average Otel 0 CPU: {avg_otel0_cpu:.2f} millicores")
    print(f"Max Otel 0 CPU: {max(parsed_otel0_cpus):.2f} millicores")

if otel0_mems:
    parsed_otel0_mems = [parse_mem(mem) for mem in otel0_mems]
    avg_otel0_mem = sum(parsed_otel0_mems) / len(parsed_otel0_mems)
    print(f"Average Otel 0 MEM: {avg_otel0_mem:.2f} Mi")
    print(f"Max Otel 0 MEM: {max(parsed_otel0_mems)} Mi")

if otel2_cpus:
    parsed_otel2_cpus = [parse_cpu(cpu) for cpu in otel2_cpus]
    avg_otel2_cpu = sum(parsed_otel2_cpus) / len(parsed_otel2_cpus)
    print(f"Average Otel 2 CPU: {avg_otel2_cpu:.2f} millicores")
    print(f"Max Otel 2 CPU: {max(parsed_otel2_cpus):.2f} millicores")

if otel2_mems:
    parsed_otel2_mems = [parse_mem(mem) for mem in otel2_mems]
    avg_otel2_mem = sum(parsed_otel2_mems) / len(parsed_otel2_mems)
    print(f"Average Otel 2 MEM: {avg_otel2_mem:.2f} Mi")
    print(f"Max Otel 2 MEM: {max(parsed_otel2_mems)} Mi")

if loki0_cpus:
    parsed_loki0_cpus = [parse_cpu(cpu) for cpu in loki0_cpus]
    avg_loki0_cpu = sum(parsed_loki0_cpus) / len(parsed_loki0_cpus)
    print(f"Average Loki 0 CPU: {avg_loki0_cpu:.2f} millicores")
    print(f"Max Loki 0 CPU: {max(parsed_loki0_cpus):.2f} millicores")

if loki0_mems:
    parsed_loki0_mems = [parse_mem(mem) for mem in loki0_mems]
    avg_loki0_mem = sum(parsed_loki0_mems) / len(parsed_loki0_mems)
    print(f"Average Loki 0 MEM: {avg_loki0_mem:.2f} Mi")
    print(f"Max Loki 0 MEM: {max(parsed_loki0_mems)} Mi")

if loki1_cpus:
    parsed_loki1_cpus = [parse_cpu(cpu) for cpu in loki1_cpus]
    avg_loki1_cpu = sum(parsed_loki1_cpus) / len(parsed_loki1_cpus)
    print(f"Average Loki 1 CPU: {avg_loki1_cpu:.2f} millicores")
    print(f"Max Loki 1 CPU: {max(parsed_loki1_cpus):.2f} millicores")

if loki1_mems:
    parsed_loki1_mems = [parse_mem(mem) for mem in loki1_mems]
    avg_loki1_mem = sum(parsed_loki1_mems) / len(parsed_loki1_mems)
    print(f"Average Loki 1 MEM: {avg_loki1_mem:.2f} Mi")
    print(f"Max Loki 1 MEM: {max(parsed_loki1_mems)} Mi")

if loki2_cpus:
    parsed_loki2_cpus = [parse_cpu(cpu) for cpu in loki2_cpus]
    avg_loki2_cpu = sum(parsed_loki2_cpus) / len(parsed_loki2_cpus)
    print(f"Average Loki 2 CPU: {avg_loki2_cpu:.2f} millicores")
    print(f"Max Loki 2 CPU: {max(parsed_loki2_cpus):.2f} millicores")

if loki2_mems:
    parsed_loki2_mems = [parse_mem(mem) for mem in loki2_mems]
    avg_loki2_mem = sum(parsed_loki2_mems) / len(parsed_loki2_mems)
    print(f"Average Loki 2 MEM: {avg_loki2_mem:.2f} Mi")
    print(f"Max Loki 2 MEM: {max(parsed_loki2_mems)} Mi")
