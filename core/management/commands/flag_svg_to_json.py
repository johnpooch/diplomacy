import json
import os
import re

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


regex = r'^.*(cls-[\d]+).*(#[\w\d]+)'


class Command(BaseCommand):

    @property
    def help(self):
        return 'Convert flag svg to json string.'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=str,
            help='SVG file to convert.',
        )

    def handle(self, *args, **options):
        svg_path = settings.BASE_DIR + '/' + options['file']
        result_dict = {}

        if not os.path.isfile(svg_path):
            raise CommandError(f'"{svg_path}" not found.')

        with open(svg_path) as f:
            content = f.read()
            soup = BeautifulSoup(content, features='lxml')

        # get viewbox
        svg = soup.find('svg')
        result_dict['viewBox'] = svg['viewbox']

        # create fill dict
        style = svg.find('style').find(text=True, recursive=False).strip()
        fills = style.split('}')
        fills_dict = {}
        for fill in fills[:-1]:
            m = re.search(regex, fill)
            k, v = m.groups()
            fills_dict[k] = v

        result_dict['paths'] = []
        paths = svg.findAll('path')
        for path in paths:
            result_dict['paths'].append(
                {
                    'fill': fills_dict[path['class'][0]],
                    'path': path['d']
                }
            )
        return json.dumps(json.dumps(result_dict))
