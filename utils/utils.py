import json


def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error soubor: {file_path} nenalezen")
        return None
    except json.JSONDecodeError:
        print(f"Error pri dekodovani: {file_path}")
        return None
        
def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
        