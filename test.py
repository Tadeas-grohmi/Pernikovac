import json


def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return None
        
def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
        
json_file_path = './utils/data.json'
json_data = read_json(json_file_path)
print(json_data["z_offset"])

json_data["z_offset"] = 5
write_json(json_file_path, json_data)

json_data = read_json(json_file_path)
print(json_data["z_offset"])