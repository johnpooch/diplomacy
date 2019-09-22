from django.test import TestCase

from service.models import Nation, Piece
from service.tests.utils import TerritoriesMixin


class TestPiece(TestCase, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json']

    def setUp(self):
        self.initialise_territories()

    def test_is_inland(self):
        nation = Nation.objects.get(name='France')
        with self.assertRaises(ValueError):
            Piece.objects.create(
                nation=nation,
                territory=self.spain,
                type=Piece.PieceType.FLEET
            )
