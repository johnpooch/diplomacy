import json

from django.conf import settings


def get_fixture_data(file_name):
    """
    Converts json fixtures into python dict.

    Args:
        * `file_name` - `str` - the name of the file e.g. 'nation.json'
    """
    with open(settings.BASE_DIR + '/fixtures/' + file_name, 'r') as f:
        data = f.read()
    return json.loads(data)
