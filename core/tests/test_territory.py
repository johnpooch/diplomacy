from django.test import TestCase

from core import factories, models
from core.models.base import Phase, Season


class TestTerritory(TestCase):

    def setUp(self):
        self.variant = factories.VariantFactory()
        self.user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game.participants.add(self.user)

    def test_contested_territory_to_dict(self):
        retreat_turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.FALL,
            year=1901,
        )
        france = models.Nation.objects.create(
            variant=self.variant,
            name='France',
        )
        models.NationState.objects.create(
            turn=retreat_turn,
            nation=france,
            user=self.user,
        )
        paris = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
        )
        paris_state = models.TerritoryState.objects.create(
            territory=paris,
            turn=retreat_turn,
        )
        data = paris_state.to_dict()
        self.assertEqual(data['contested'], False)
        paris_state.contested = True
        paris_state.save()
        data = paris_state.to_dict()
        self.assertEqual(data['contested'], True)
