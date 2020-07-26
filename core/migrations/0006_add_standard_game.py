from copy import deepcopy
import json

from django.conf import settings
from django.db import migrations


def get_fixture_data(location, file_name):
    with open('/'.join([settings.BASE_DIR, location, file_name]), 'r') as f:
        json_data = f.read()
    return json.loads(json_data)


def add_standard_game_data(apps, schema_editor):
    nation_map = {}
    territory_map = {}
    named_coast_map = {}

    location = 'core/migrations/fixtures'
    Variant = apps.get_model('core', 'Variant')
    Nation = apps.get_model('core', 'Nation')
    Territory = apps.get_model('core', 'Territory')
    MapData = apps.get_model('core', 'MapData')
    TerritoryMapData = apps.get_model('core', 'TerritoryMapData')
    NamedCoast = apps.get_model('core', 'NamedCoast')
    NamedCoastMapData = apps.get_model('core', 'NamedCoastMapData')

    variant_data = get_fixture_data(location, 'variant.json')[0]['fields']
    variant = Variant.objects.create(**variant_data)

    nation_data = get_fixture_data(location, 'nation.json')
    for item in nation_data:
        nation_pk = item['pk']
        data = item['fields']
        data['variant'] = variant
        nation = Nation.objects.create(**data)
        nation_map[nation_pk] = nation

    territory_data = get_fixture_data(location, 'territory.json')
    for item in territory_data:
        territory_pk = item['pk']
        data = deepcopy(item['fields'])
        data['variant'] = variant
        data.pop('neighbours')
        data.pop('shared_coasts')
        controlled_by_initial = data['controlled_by_initial']
        if controlled_by_initial:
            data['controlled_by_initial'] = nation_map[controlled_by_initial]
            data['nationality'] = nation_map[controlled_by_initial]
        territory = Territory.objects.create(**data)
        territory_map[territory_pk] = territory

    for item in territory_data:
        territory_pk = item['pk']
        data = item['fields']
        neighbour_ids = data['neighbours']
        shared_coast_ids = data['shared_coasts']
        neighbours = [territory_map[i] for i in neighbour_ids]
        shared_coasts = [territory_map[i] for i in shared_coast_ids]
        territory = territory_map[territory_pk]
        territory.neighbours.set(neighbours)
        territory.shared_coasts.set(shared_coasts)

    map_data_data = get_fixture_data(location, 'map_data.json')[0]['fields']
    map_data_data['variant'] = variant
    map_data = MapData.objects.create(**map_data_data)

    territory_map_data = get_fixture_data(location, 'territory_map_data.json')

    for item in territory_map_data:
        data = item['fields']
        data['map_data'] = map_data
        territory = data.get('territory')
        if territory:
            data['territory'] = territory_map[territory]
        TerritoryMapData.objects.create(**data)

    named_coast_data = get_fixture_data(location, 'named_coast.json')
    for item in named_coast_data:
        named_coast_pk = item['pk']
        data = deepcopy(item['fields'])
        data['parent'] = territory_map[data['parent']]
        data.pop('neighbours')
        named_coast = NamedCoast.objects.create(**data)
        named_coast_map[named_coast_pk] = named_coast

    for item in named_coast_data:
        named_coast_pk = item['pk']
        data = item['fields']
        neighbour_ids = data['neighbours']
        neighbours = [territory_map[i] for i in neighbour_ids]
        named_coast = named_coast_map[named_coast_pk]
        named_coast.neighbours.set(neighbours)

    named_coast_map_data = get_fixture_data(location, 'named_coast_map_data.json')

    for item in named_coast_map_data:
        data = item['fields']
        data['map_data'] = map_data
        named_coast = data.get('named_coast')
        if named_coast:
            data['named_coast'] = named_coast_map[named_coast]
        NamedCoastMapData.objects.create(**data)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_merge_20200726_1240'),
    ]

    operations = [
        migrations.RunPython(
            add_standard_game_data,
            reverse_code=migrations.RunPython.noop
        ),
    ]
