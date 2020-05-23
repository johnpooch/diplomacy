import json
import os
import unittest

from django.conf import settings
from django.core.management import call_command

from service.utils import text_to_order_data

GAME_DIR = settings.BASE_DIR + '/order_histories/game_1'


class TestConvertOrderHistoryToData(unittest.TestCase):

    def test_game_1(self):
        call_command(
            'convert_order_histories_to_data',
            'order_histories/game_1',
        )
