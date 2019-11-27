from pprint import pprint

from django.test import TestCase

from core import factories
from service.serializers import GameStateSerializer


class TestGameStateSerializer(TestCase):

    def test_game_state(self):
        participants = [
            factories.UserFactory(username='User 1'),
        ]
        variant = factories.VariantFactory()
        territory = factories.TerritoryFactory(variant=variant)
        game = factories.GameFactory(
            num_players=2,
            participants=participants,
            variant=variant,
        )
        turn = factories.TurnFactory(game=game)
        territory_state = factories.TerritoryStateFactory(
            turn=turn,
            territory=territory,
        ),
        serializer = GameStateSerializer(game)
        pprint(serializer.data)
