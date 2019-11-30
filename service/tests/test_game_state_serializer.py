from pprint import pprint

from django.test import TestCase

from core import factories
from service.serializers import GameStateSerializer


class TestGameStateSerializer(TestCase):

    def test_game_state(self):
        game = factories.StandardGameFactory()
        serializer = GameStateSerializer(game)
        pprint(serializer.data)
