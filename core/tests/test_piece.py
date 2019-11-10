from core import models
from core.models.base import CommandType, PieceType
from core.tests.base import HelperMixin, TerritoriesMixin
from core.tests.base import InitialGameStateTestCase as TestCase


class TestPieceClean(TestCase, TerritoriesMixin):

    fixtures = ['game.json', 'turn.json', 'nations.json', 'territories.json',
                'named_coasts.json']

    def setUp(self):
        self.game = models.Game.objects.get()
        self.turn = models.Turn.objects.get()
        self.initialise_territories()

    def test_fleet_cannot_be_in_complex_territory_and_not_named_coast(self):
        nation = models.Nation.objects.get(name='France')
        with self.assertRaises(ValueError):
            models.Piece.objects.create(
                turn=self.turn,
                nation=nation,
                territory=self.spain,
                type=PieceType.FLEET
            )

    def test_fleet_cannot_be_in_inland_territory(self):
        nation = models.Nation.objects.get(name='France')
        with self.assertRaises(ValueError):
            models.Piece.objects.create(
                turn=self.turn,
                nation=nation,
                territory=self.paris,
                type=PieceType.FLEET
            )

    def test_army_cannot_be_on_named_coast(self):
        nation = models.Nation.objects.get(name='France')
        spain_nc = models.NamedCoast.objects.get(name='spain north coast')
        with self.assertRaises(ValueError):
            models.Piece.objects.create(
                turn=self.turn,
                nation=nation,
                territory=self.spain,
                named_coast=spain_nc,
                type=PieceType.ARMY
            )


class TestIsPieceType(TestCase):

    fixtures = ['game.json', 'turn.json', 'nations.json', 'territories.json',
                'pieces.json']

    def test_army_is_not_fleet(self):
        piece = models.Piece.objects.get(territory__name='marseilles')
        self.assertFalse(piece.is_fleet)

    def test_fleet_is_not_army(self):
        piece = models.Piece.objects.get(territory__name='brest')
        self.assertFalse(piece.is_army)

    def test_army_is_fleet(self):
        piece = models.Piece.objects.get(territory__name='marseilles')
        self.assertTrue(piece.is_army)

    def test_fleet_is_fleet(self):
        piece = models.Piece.objects.get(territory__name='brest')
        self.assertTrue(piece.is_fleet)


class TestDislodged(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['game.json', 'turn.json', 'nations.json', 'territories.json',
                'pieces.json']

    def setUp(self):
        self.game = models.Game.objects.get()
        self.turn = models.Turn.objects.get()
        self.initialise_territories()
        germany = models.Nation.objects.get(name='Germany')
        self.defending_army = models.Piece.objects.get(territory=self.paris)
        self.attacking_army = models.Piece.objects.create(
            turn=self.turn,
            nation=germany,
            territory=self.burgundy,
            type=PieceType.ARMY,
        )
        self.supporting_army = models.Piece.objects.create(
            turn=self.turn,
            nation=germany,
            territory=self.picardy,
            type=PieceType.ARMY,
        )
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.german_order = models.Order.objects.create(
            nation=germany,
            turn=self.turn,
        )

    def test_no_attacking_piece_not_dislodged(self):
        """
        If there is no attacking piece, the defending piece is not dislodged.
        """
        self.hold(self.defending_army, self.paris).save()
        self.assertFalse(self.defending_army.dislodged)

    def test_one_attacking_piece_not_dislodged(self):
        """
        If there is only one attacking piece with no support, the defending
        piece is not dislodged.
        """
        self.hold(self.defending_army, self.paris).save()
        models.Command.objects.create(
            piece=self.attacking_army,
            source=self.burgundy,
            target=self.paris,
            order=self.german_order,
            type=CommandType.MOVE
        )
        self.assertFalse(self.defending_army.dislodged)

    def test_attacking_piece_with_support_causes_dislodge(self):
        """
        If the attacking piece has support and the defending piece doesn't, the
        defending piece is dislodged.
        """
        self.hold(self.defending_army, self.paris).save()
        models.Command.objects.create(
            piece=self.attacking_army,
            source=self.burgundy,
            target=self.paris,
            order=self.german_order,
            type=CommandType.MOVE
        )
        models.Command.objects.create(
            piece=self.supporting_army,
            source=self.picardy,
            target=self.paris,
            aux=self.burgundy,
            order=self.german_order,
            type=CommandType.SUPPORT,
        )
        models.Command.objects.process()
        self.defending_army.refresh_from_db()
        self.assertTrue(self.defending_army.dislodged)

    def test_moving_piece_not_dislodged(self):
        """
        If the defending piece successfully moves, it cannot be dislodged.
        """
        self.move(self.defending_army, self.paris, self.gascony).save()
        models.Command.objects.create(
            piece=self.attacking_army,
            source=self.burgundy,
            target=self.paris,
            order=self.german_order,
            type=CommandType.MOVE
        )
        models.Command.objects.create(
            piece=self.supporting_army,
            source=self.picardy,
            target=self.paris,
            aux=self.burgundy,
            order=self.german_order,
            type=CommandType.SUPPORT,
        )
        self.assertFalse(self.defending_army.dislodged)

    def test_attacking_piece_with_cancelled_support_not_dislodged(self):
        """
        If the attacking piece has support but the support is cut, the
        defending piece is not dislodged.
        """
        pass
