from copy import deepcopy
import json

from django.conf import settings
from django.db import migrations
from django.utils.text import slugify


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
    NamedCoast = apps.get_model('core', 'NamedCoast')

    variant_data = get_fixture_data(location, 'variant.json')[0]['fields']
    variant = Variant.objects.create(**variant_data)

    nation_data = get_fixture_data(location, 'nation.json')
    for item in nation_data:
        nation_pk = item['pk']
        data = item['fields']
        data['variant'] = variant
        data['id'] = slugify('-'.join([variant.name, data['name']]))
        nation = Nation.objects.create(**data)
        nation_map[nation_pk] = nation

    territory_data = get_fixture_data(location, 'territory.json')
    for item in territory_data:
        territory_pk = item['pk']
        data = deepcopy(item['fields'])
        data['variant'] = variant
        data['id'] = slugify('-'.join([variant.name, data['name']]))
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

    named_coast_data = get_fixture_data(location, 'named_coast.json')
    for item in named_coast_data:
        named_coast_pk = item['pk']
        data = deepcopy(item['fields'])
        data['parent'] = territory_map[data['parent']]
        data['id'] = slugify('-'.join([data['parent'].variant.name, data['name']]))
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
        named_coast = data.get('named_coast')
        if named_coast:
            data['named_coast'] = named_coast_map[named_coast]


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_standard_game_data,
            reverse_code=migrations.RunPython.noop
        ),
    ]
