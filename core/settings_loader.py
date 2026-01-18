import yaml

def load_settings():
    with open("config/settings.yaml") as file:
        return yaml.safe_load(file)