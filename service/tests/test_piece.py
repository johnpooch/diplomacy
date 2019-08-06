from django.test import TestCase

from service.models import Nation, Piece
from service.tests.base import TerritoriesMixin


class TestPiece(TestCase, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json']

    def setUp(self):
        self.initialise_territories()

    def test_fleet_cannot_be_in_complex_territory_and_not_named_coast(self):
        nation = Nation.objects.get(name='France')
        with self.assertRaises(ValueError):
            Piece.objects.create(
                nation=nation,
                territory=self.spain,
                type=Piece.PieceType.FLEET
            )

    def test_fleet_cannot_be_in_inland_territory(self):
        nation = Nation.objects.get(name='France')
        with self.assertRaises(ValueError):
            Piece.objects.create(
                nation=nation,
                territory=self.paris,
                type=Piece.PieceType.FLEET
            )
