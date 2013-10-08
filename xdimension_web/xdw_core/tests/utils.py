import os


def get_test_data(name):
    with open(os.path.join(os.path.dirname(__file__), 'data', name)) as f:
        return f.read()
