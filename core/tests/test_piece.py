from django.test import TestCase

from service.models import NamedCoast, Nation, Piece
from service.tests.base import TerritoriesMixin


class TestPieceClean(TestCase, TerritoriesMixin):

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

    def test_army_cannot_be_on_named_coast(self):
        nation = Nation.objects.get(name='France')
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        with self.assertRaises(ValueError):
            Piece.objects.create(
                nation=nation,
                territory=self.spain,
                named_coast=spain_nc,
                type=Piece.PieceType.ARMY
            )


class TestIsPieceType(TestCase):

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def test_army_is_not_fleet(self):
        piece = Piece.objects.get(territory__name='marseilles')
        self.assertFalse(piece.is_fleet())

    def test_fleet_is_not_army(self):
        piece = Piece.objects.get(territory__name='brest')
        self.assertFalse(piece.is_army())

    def test_army_is_fleet(self):
        piece = Piece.objects.get(territory__name='marseilles')
        self.assertTrue(piece.is_army())

    def test_fleet_is_fleet(self):
        piece = Piece.objects.get(territory__name='brest')
        self.assertTrue(piece.is_fleet())
