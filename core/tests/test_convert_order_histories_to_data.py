from unittest import skip
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


GAME_DIR = settings.BASE_DIR + '/order_histories/game_1'


class TestConvertOrderHistoryToData(TestCase):

    fixtures = [
        'dev/variant',
        'dev/nation',
        'dev/territory',
        'dev/named_coast',
    ]

    @skip
    def test_game_1(self):
        call_command(
            'convert_order_histories_to_data',
            'order_histories/game_1',
        )
