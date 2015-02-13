import yaml

def parse_checkmate_settings(content):
    """
    Currently we only parse the YAML file. In the future we might perform additional checks.
    """
    output = yaml.load(content)
    return output