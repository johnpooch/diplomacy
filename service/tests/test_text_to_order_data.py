import json
import os
import unittest

from service.utils import text_to_order_data

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

data_folder = WORKING_DIRECTORY + '/order_histories/'


class TestConvertTextToData(unittest.TestCase):

    def test_game_1_spring_1901(self):
        game_dir = 'game_1/'
        file_to_open = data_folder + game_dir + 'spring_1901.txt'
        with open(file_to_open) as f:
            text = f.read()
        jason = text_to_order_data(text)
        data = json.loads(jason)
        expected_order = {
            'source': 'edinburgh',
            'type': 'move',
            'target': 'norwegian sea',
            'nation': 'England'
        }
        self.assertEqual(len(data), 22)
        self.assertEqual(data[0]['order'], expected_order)
        self.assertEqual(data[0]['outcome'], 'resolved')

