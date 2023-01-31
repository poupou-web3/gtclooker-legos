import yaml

def read_yaml(yaml_file):
    """
    This function takes in a yaml file path and returns the data loaded from the file
    """
    with open(yaml_file, 'r') as content:
        data_loaded = yaml.safe_load(content)

    return data_loaded

def split(list_a, chunk_size):

    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]