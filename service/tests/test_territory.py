from django.db.models import QuerySet

from service.models import Command, Nation, Order, Piece
from service.tests.base import TerritoriesMixin, HelperMixin
from service.tests.base import InitialGameStateTestCase as TestCase


class TestTerritory(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        self.initialise_territories()

    def test_is_complex(self):
        self.assertTrue(self.spain.is_complex())

    def test_is_not_complex(self):
        self.assertFalse(self.brest.is_complex())

    def test_is_inland(self):
        self.assertTrue(self.paris.is_inland())

    def test_is_not_inland(self):
        self.assertFalse(self.brest.is_inland())


class TestAttackingPieces(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.attacking_army = Piece.objects.get(territory__name='paris')
        self.attacking_fleet = Piece.objects.get(territory__name='brest')

    def test_attacking_pieces(self):
        """
        ``territory.attacking_pieces`` returns a queryset of pieces which are
        moving into the territory.
        """
        Command.objects.create(
            source=self.paris,
            piece=self.attacking_army,
            target=self.picardy,
            type=Command.CommandTypes.MOVE,
            order=self.order
        )
        attacking_pieces = self.picardy.attacking_pieces
        self.assertEqual(len(attacking_pieces), 1)
        self.assertTrue(isinstance(attacking_pieces, QuerySet))

    def test_attacking_pieces_no_attacking_pieces(self):
        """
        ``territory.attacking_pieces`` returns an empty queryset of pieces when
        no pieces are moving into that territory.
        """
        attacking_pieces = self.picardy.attacking_pieces
        self.assertEqual(len(attacking_pieces), 0)
        self.assertTrue(isinstance(attacking_pieces, QuerySet))

    def test_multiple_attacking_pieces(self):
        """
        ``territory.attacking_pieces`` returns a queryset of pieces which are
        moving into the territory when multiple pieces are moving in.
        """
        Command.objects.create(
            source=self.paris,
            piece=self.attacking_army,
            target=self.picardy,
            type=Command.CommandTypes.MOVE,
            order=self.order
        )
        Command.objects.create(
            source=self.brest,
            piece=self.attacking_fleet,
            target=self.picardy,
            type=Command.CommandTypes.MOVE,
            order=self.order
        )
        attacking_pieces = self.picardy.attacking_pieces
        self.assertEqual(len(attacking_pieces), 2)
        self.assertTrue(isinstance(attacking_pieces, QuerySet))


class TestForeignAttackingPieces(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()

        self.france = Nation.objects.get(name='France')
        self.germany = Nation.objects.get(name='Germany')

        self.french_order = Order.objects.create(
            nation=self.france,
            turn=self.turn,
        )
        self.german_order = Order.objects.create(
            nation=self.germany,
            turn=self.turn,
        )
        self.friendly_attacking_army = Piece.objects\
            .get(territory__name='paris')
        self.foreign_attacking_army = Piece.objects\
            .get(territory__name='munich')

    def test_foreign_attacking_pieces(self):
        """
        ``territory.foreign_attacking_pieces`` returns a queryset of pieces
        which are moving into the territory and do not belong to the given
        ``nation``.
        """
        # French command
        Command.objects.create(
            source=self.paris,
            piece=self.friendly_attacking_army,
            target=self.burgundy,
            type=Command.CommandTypes.MOVE,
            order=self.french_order
        )
        # German command
        Command.objects.create(
            source=self.munich,
            piece=self.foreign_attacking_army,
            target=self.burgundy,
            type=Command.CommandTypes.MOVE,
            order=self.german_order
        )
        attacking_pieces = self.burgundy.attacking_pieces
        foreign_attacking_pieces = self.burgundy\
            .foreign_attacking_pieces(self.france)
        self.assertEqual(len(attacking_pieces), 2)
        self.assertEqual(len(foreign_attacking_pieces), 1)
        self.assertTrue(isinstance(foreign_attacking_pieces, QuerySet))
