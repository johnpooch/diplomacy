from django.test import TestCase

from core.models import Nation, Piece
from core.models.base import PieceType
from core.tests.base import TerritoriesMixin


class TestTerritory(TestCase, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json']

    def setUp(self):
        self.initialise_territories()

    def test_is_inland(self):
        nation = Nation.objects.get(name='France')
        with self.assertRaises(ValueError):
            Piece.objects.create(
                nation=nation,
                territory=self.spain,
                type=PieceType.FLEET
            )
