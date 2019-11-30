import json

from django.conf import settings


def get_territory_data():
    """
    Converts territory json fixture into python dict.
    """
    with open(settings.BASE_DIR + '/fixtures/territories.json', 'r') as f:
        data=f.read()
    return json.loads(data)