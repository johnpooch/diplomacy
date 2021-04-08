from django.test import TestCase

from core import factories, models


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
