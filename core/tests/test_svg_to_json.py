from io import StringIO
import json

from django.core.management import call_command
from django.test import TestCase

test_svg_path = 'core/tests/data/simple_flag.svg'


class TestSvgToJson(TestCase):

    def setUp(self):
        pass

    def test_command_output(self):
        out = StringIO()
        call_command('flag_svg_to_json', test_svg_path, stdout=out)

        expected_data = {
            "viewBox": "0 0 252.39 168.26",
            "paths": [
                {
                    "fill": "#5d9240",
                    "path": "M0,0H84.13V168.26H0Z"
                },
                {
                    "fill": "#f0efef",
                    "path": "M84.13,0h84.13V168.26H84.13Z"
                }
            ]
        }
        returned_data = json.loads(json.loads(out.getvalue()))
        self.assertEqual(expected_data, returned_data)
