import os

def asset(path):
    return os.path.join(os.path.dirname(__file__), "..", "inputs", path)
