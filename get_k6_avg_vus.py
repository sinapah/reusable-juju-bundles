import subprocess
import re

vus_samples = []

proc = subprocess.Popen(
    ["/home/ubuntu/repos/opentelemetry-collector-k8s-k6-load-tests/k6", "run", "/home/ubuntu/repos/opentelemetry-collector-k8s-k6-load-tests/scripts/constant-arrival-rate-scenario.js"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True
)

for line in proc.stdout:
    print(line, end='')  # showing the live output
    match = re.search(r'(\d+)/\d+ VUs', line)
    if match:
        vus = int(match.group(1))
        vus_samples.append(vus)

# After test finishes
if vus_samples:
    avg = sum(vus_samples) / len(vus_samples)
    print(f"\nAverage VUs: {avg:.2f}")