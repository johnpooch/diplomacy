import os
import unittest

from adjudicator.state import validate_json

TEST_JSON_DIR = os.path.dirname(os.path.realpath(__file__)) + '/test_json/'


class TestValidateJSON(unittest.TestCase):

    def test_simple_validate_json(self):
        file_to_open = TEST_JSON_DIR + 'simple_data.json'
        with open(file_to_open) as file:
            json_data = file.read()
        validate_json(json_data)

    def test_invalid_phase(self):
        file_to_open = TEST_JSON_DIR + 'invalid_phase.json'
        with open(file_to_open) as file:
            json_data = file.read()
        with self.assertRaises(ValueError) as e:
            validate_json(json_data)
        self.assertEqual(
            str(e.exception),
            'Invalid game state - "phase" must be one of "order", "retreat", or "build"'
        )

    def test_invalid_order_for_order_phase(self):
        file_to_open = TEST_JSON_DIR + 'invalid_order_for_order_phase.json'
        with open(file_to_open) as file:
            json_data = file.read()
        with self.assertRaises(ValueError) as e:
            validate_json(json_data)
        self.assertEqual(
            str(e.exception),
            'Invalid game state - during order phase, each order must be one of "hold", "move", "support", or "convoy"'
        )

    def test_invalid_order_for_retreat_phase(self):
        file_to_open = TEST_JSON_DIR + 'invalid_order_for_retreat_phase.json'
        with open(file_to_open) as file:
            json_data = file.read()
        with self.assertRaises(ValueError) as e:
            validate_json(json_data)
        self.assertEqual(
            str(e.exception),
            'Invalid game state - during retreat phase, each order must be one of "retreat" or "disband"'
        )
