import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    @property
    def help(self):
        return 'Convert json file to territory map data.'

    def add_arguments(self, parser):
        parser.add_argument(
            'infile',
            type=str,
            help='File to load data from.',
        )
        parser.add_argument(
            'outfile',
            type=str,
            help='File to dump data to.',
        )
        parser.add_argument(
            'territoriesfile',
            type=str,
            help='File to match pks against.',
        )
        parser.add_argument(
            '--indent', type=int,
            help='Specifies the indent level to use when printing output.',
        )

    def handle(self, *args, **options):
        in_file = settings.BASE_DIR + '/' + options['infile']
        out_file = settings.BASE_DIR + '/' + options['outfile']
        territories_file = settings.BASE_DIR + '/' + options['territoriesfile']

        if not os.path.isfile(in_file):
            raise CommandError(f'"{in_file}" not found.')
        if not os.path.isdir(os.path.dirname(out_file)):
            raise CommandError(
                f'Cannot write to "{os.path.dirname(out_file)}", directory not '
                'found.'
            )

        with open(in_file) as f:
            data = json.load(f)

        with open(territories_file) as f:
            territories_file_data = json.load(f)

        for t in territories_file_data:
            found_name = False
            name = t['fields']['name']
            for territory_data in data['territories'].values():
                jdip_name = territory_data.get('name')
                if jdip_name:
                    if jdip_name.lower() == name:
                        territory_data['pk'] = t['pk']
                        found_name = True
                        break
            if not found_name:
                raise Exception(
                    'Territories in territories file that do not have a '
                    'corresponding territory in the infile.'
                )
        out_data = []
        for i, territory_data in enumerate(data['territories'].values()):
            name = territory_data.get('name')
            typ = territory_data['type']
            # convert to our terminology
            if typ == 'water':
                typ = 'sea'
            if typ == 'neutral':
                typ = 'land'
            fields = {
                'map_data': 1,
                'name': name,
                'type': typ,
                'abbreviation': territory_data.get('abbreviation'),
                'path': territory_data['path'],
                'text_x': territory_data.get('text', {}).get('x'),
                'text_y': territory_data.get('text', {}).get('y'),
                'piece_x': territory_data.get('piece', {}).get('x'),
                'piece_y': territory_data.get('piece', {}).get('y'),
                'supply_center_x': territory_data.get('supplyCenter', {}).get('x'),
                'supply_center_y': territory_data.get('supplyCenter', {}).get('y'),
                'dislodged_piece_x': territory_data.get('dislodgedPiece', {}).get('x'),
                'dislodged_piece_y': territory_data.get('dislodgedPiece', {}).get('y'),
            }
            pk = territory_data.get('pk')
            if pk:
                fields['territory'] = pk

            out_item = {
                'model': 'core.territorymapdata',
                'pk': i + 1,
                'fields': fields,
            }

            out_data.append(out_item)

        with open(out_file, 'w') as f:
            json.dump(out_data, f, indent=options.get('indent'), separators=(',', ': '))
