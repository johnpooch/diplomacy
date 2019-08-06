from .base import InitialGameStateTestCase as TestCase

from service.models import Piece


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
