import json
from cosl import LZMABase64
import sys

def load_dashboard_dict(filename):
    # Read the base64-compressed content from the file named "b64"
    with open(filename, "r", encoding="utf-8") as f:
        compressed_content = f.read().strip()

    # Decompress using LZMABase64
    dashboard_json = LZMABase64.decompress(compressed_content)

    # Parse JSON into a Python dictionary
    dashboard_dict = json.loads(dashboard_json)

    return dashboard_dict


if __name__ == "__main__":
    filename = sys.argv[1]
    dashboard_dict = load_dashboard_dict(filename)
    print(dashboard_dict)

