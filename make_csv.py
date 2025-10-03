import csv
import re
import sys

args = dict(arg.split('=') for arg in sys.argv[1:])
input_file = args.get('input')
output_file = args.get('output')

data = []
current_package = None
current_version = None

with open(input_file, 'r') as file:
    for line in file:
        line = line.strip()

        if line.startswith("Version:"):
            current_version = line.split(":", 1)[1].strip()
        elif line.startswith("Repository:"):
            current_package = line.split(":", 1)[1].strip()
            if current_package and current_version:
                data.append({
                    'PACKAGE': current_package,
                    'VERSION': current_version
                })
            current_package = None
            current_version = None

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['PACKAGE', 'VERSION'])
    writer.writeheader()
    writer.writerows(data)
