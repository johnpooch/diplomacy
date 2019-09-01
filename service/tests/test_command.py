from django.core.exceptions import ValidationError

from service.command_validator import ArmyMoveValidator, FleetMoveValidator, \
    get_command_validator
from service.models import Challenge, Move, NamedCoast, Nation, Order, Piece
from service.tests.base import HelperMixin, TerritoriesMixin
from .base import InitialGameStateTestCase as TestCase


class TestClean(TestCase, HelperMixin, TerritoriesMixin):
    
    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_raises_value_error_when_move_invalid(self):
        """
        """
        command = self.move(self.paris, self.english_channel)
        with self.assertRaises(ValueError):
            command.save()


class TestFleetMoveClean(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = Piece.objects.get(territory__name='brest')

    def test_sea_to_adjacent_sea_territory(self):
        """
        Fleet can move to adjacent sea territory.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        command = self.move(self.english_channel, self.irish_sea)
        self.assertTrue(command.clean())

    def test_sea_to_adjacent_coastal_territory(self):
        """
        Fleet can move from sea territory to adjacent coastal territory.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        command = self.move(self.english_channel, self.brest)
        self.assertTrue(command.clean())

    def test_coastal_to_adjacent_coastal_territory_if_shared_coast(self):
        """
        Fleet can move from coastal territory to adjacent coastal territory.
        """
        self.set_piece_territory(self.fleet, self.brest)
        command = self.move(self.brest, self.gascony)
        self.assertTrue(command.clean())

    def test_coastal_to_adjacent_coastal_territory_if_not_shared_coast(self):
        """
        Fleet cannot move from coastal territory to adjacent coastal territory
        when no shared coastline.
        """
        Piece.objects.get(territory__name='marseilles').delete()
        self.set_piece_territory(self.fleet, self.marseilles)
        command = self.move(self.marseilles, self.gascony)
        with self.assertRaises(ValidationError):
            command.clean()

    def test_coastal_to_adjacent_inland_territory(self):
        """
        Fleet cannot move from coastal territory to adjacent inland territory.
        """
        Piece.objects.get(territory__name='marseilles').delete()
        self.set_piece_territory(self.fleet, self.marseilles)
        command = self.move(self.marseilles, self.burgundy)
        with self.assertRaises(ValidationError):
            command.clean()

    def test_cannot_move_to_complex_territory_and_not_named_coast(self):
        """
        A fleet cannot move to a complex territory without specifying which
        named coast.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        command = self.move(
            self.mid_atlantic,
            self.spain,
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_can_move_to_complex_territory_with_named_coast(self):
        """
        A fleet can move to a complex territory if specifying which named
        coast.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        command = self.move(
            self.mid_atlantic,
            self.spain,
            target_coast=spain_nc
        )
        self.assertTrue(command.clean())

    def test_cannot_move_to_non_adjacent_named_coast(self):
        """
        A fleet cannot move to a named coast of a complex territory if the
        source territory is not a neighbour of the named coast.
        """
        self.set_piece_territory(self.fleet, self.western_mediterranean)
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        command = self.move(
            self.western_mediterranean,
            self.spain,
            target_coast=spain_nc
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_cannot_move_from_named_coast_to_non_neighbour(self):
        """
        A fleet cannot move from a named coast of a complex territory if the
        target territory is not a neighbour of the named coast.
        """
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        self.set_piece_territory(self.fleet, self.spain, named_coast=spain_nc)
        command = self.move(
            self.spain,
            self.western_mediterranean,
            source_coast=spain_nc
        )
        with self.assertRaises(ValidationError):
            command.clean()


class TestArmyMoveClean(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.army = Piece.objects.get(territory__name='marseilles')

    def test_coastal_to_adjacent_coastal_territory_shared_coast(self):
        """
        Army can move from a coastal territory to an adjacent coastal territory
        when there is a shared coast.
        """
        command = self.move(self.marseilles, self.piedmont)
        self.assertTrue(command.clean())

    def test_coastal_to_adjacent_coastal_territory_no_shared_coast(self):
        """
        Army can move from coastal territory to adjacent coastal territory when
        no shared coast.
        """
        command = self.move(self.marseilles, self.gascony)
        self.assertTrue(command.clean())

    def test_coastal_to_adjacent_inland_territory(self):
        """
        Army can move from coastal territory to adjacent inland territory.
        """
        command = self.move(self.marseilles, self.burgundy)
        self.assertTrue(command.clean())

    def test_inland_to_adjacent_inland_territory(self):
        """
        Army can move from inland territory to adjacent inland territory.
        """
        command = self.move(self.paris, self.burgundy)
        self.assertTrue(command.clean())

    def test_inland_to_adjacent_coastal_territory(self):
        """
        Army can move from inland territory to adjacent coastal territory.
        """
        command = self.move(self.paris, self.picardy)
        self.assertTrue(command.clean())

    def test_coastal_to_adjacent_sea_territory(self):
        """
        Army cannot move from coastal to adjacent sea territory.
        """
        command = self.move(self.marseilles, self.gulf_of_lyon)
        with self.assertRaises(ValidationError):
            command.clean()

    def test_coastal_to_non_adjacent_coastal_territory(self):
        """
        Army can move from a coastal territory to a non adjacent coastal
        territory via a convoy.
        """
        self.set_piece_territory(self.army, self.gascony)
        command = self.move(self.gascony, self.picardy)
        self.assertTrue(command.clean())

    def test_inland_to_non_adjacent_inland_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent inland
        territory.
        """
        self.set_piece_territory(self.army, self.burgundy)
        command = self.move(self.burgundy, self.silesia)
        with self.assertRaises(ValidationError):
            command.clean()

    def test_inland_to_non_adjacent_coastal_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent coastal
        territory.
        """
        self.set_piece_territory(self.army, self.silesia)
        command = self.move(self.silesia, self.gascony)
        with self.assertRaises(ValidationError):
            command.clean()


class TestCreateChallenge(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_army_move_creates_challenge(self):
        """
        The ``process()`` method on a valid army move command will create a
        challenge.
        """
        command = self.move(self.paris, self.burgundy)
        self.assertEqual(Challenge.objects.count(), 0)
        command.process()
        self.assertEqual(Challenge.objects.count(), 1)

        # challenge created with correct piece and target
        challenge = Challenge.objects.get()
        piece = Piece.objects.get(territory=self.paris)
        self.assertEqual(piece, challenge.piece)
        self.assertEqual(self.burgundy, challenge.territory)

    def test_fleet_move_creates_challenge(self):
        """
        The ``process()`` method on a valid fleet move command will create a
        challenge.
        """
        command = self.move(self.brest, self.english_channel)
        self.assertEqual(Challenge.objects.count(), 0)
        command.process()
        self.assertEqual(Challenge.objects.count(), 1)


class TestSupportChallenge(TestCase, HelperMixin, TerritoriesMixin):

    # TODO test support validity

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_army_support_challenge(self):
        """
        The ``process()`` method on a valid army support command will add a
        support to a challenge.
        """
        pass
