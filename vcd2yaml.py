import json
import yaml
import sys
from vcd2json import WaveExtractor

# This function parses the JSON data and extracts the "name","wave" and "data" fields
# of each signal, ignoring empty lists and objects without a "name" field
def parse_json(data):
    result = {}
    for item in data:
        if isinstance(item, dict):
            name = item.get("name")
            if name:
                wave = item.get("wave")
                result[name] = {"wave": wave}
                if "data" in item:
                    result[name]["data"] = item["data"]
        elif isinstance(item, list):
            sub_result = parse_json(item)
            if sub_result:
                result.update(sub_result)
    return result

# This function recursively traverses the dictionary and generates the YAML output
def traverse_dict(d, indent=0):
    yaml_data = ""
    for key, value in d.items():
        if isinstance(value, dict):
            yaml_data += " " * indent + f"{key}:\n"
            yaml_data += traverse_dict(value, indent + 2)
        elif isinstance(value, str) and key == "data":
            data_values = value.split()
            yaml_data += " " * indent + f"{key}:\n"
            for data_value in data_values:
                yaml_data += " " * (indent + 2) + f"- {data_value}\n"
        else:
            yaml_data += " " * indent + f"{key}: {value}\n"
    return yaml_data


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py filename.vcd")
        sys.exit(1)

    filename = sys.argv[1]

    extractor = WaveExtractor(filename, f"{filename.split('.')[0]}.json", [])
    extractor.wave_chunk = 30000
    extractor.execute()

    with open(f"{filename.split('.')[0]}.json") as f:
        data = json.load(f)

    signals = data.get("signal", [])
    result = parse_json(signals)

    yaml_data = traverse_dict(result)

    # write to file
    with open(f"{filename.split('.')[0]}.yaml", 'w') as yaml_file:
        yaml_file.write(yaml_data)
