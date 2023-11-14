import json

def load_settings(filePath='configuration/configuration.json'):
    with open(filePath, 'r') as f:
        return json.load(f)