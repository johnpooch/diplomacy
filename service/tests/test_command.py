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

    def test_raises_validation_error_when_move_invalid(self):
        """
        """
        command = self.move_command(self.paris, self.english_channel)
        with self.assertRaises(ValueError):
            command.save()


class TestFleetMoveValid(TestCase, TerritoriesMixin, HelperMixin):

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
        self.assertTrue(command.is_valid())

    def test_sea_to_adjacent_coastal_territory(self):
        """
        Fleet can move from sea territory to adjacent coastal territory.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        command = self.move_command(self.english_channel, self.brest)
        self.assertTrue(command.is_valid())

    # def test_coastal_to_adjacent_coastal_territory_if_shared_coast(self):
    #     """
    #     Fleet can move from coastal territory to adjacent coastal territory.
    #     """
    #     self.set_piece_territory(self.fleet, self.brest)
    #     command = self.move_command(self.brest, self.gascony)
    #     self.assertTrue(command.is_valid())

    # def test_coastal_to_adjacent_coastal_territory_if_not_shared_coast(self):
    #     """
    #     Fleet cannot move from coastal territory to adjacent coastal territory
    #     when no shared coastline.
    #     """
    #     Piece.objects.get(territory__name='marseilles').delete()
    #     self.set_piece_territory(self.fleet, self.marseilles)
    #     command = self.move_command(self.marseilles, self.gascony)
    #     validator = get_command_validator(command)
    #     with self.assertRaises(ValidationError):
    #         validator.is_valid()

    # def test_coastal_to_adjacent_inland_territory(self):
    #     """
    #     Fleet cannot move from coastal territory to adjacent inland territory.
    #     """
    #     Piece.objects.get(territory__name='marseilles').delete()
    #     self.set_piece_territory(self.fleet, self.marseilles)
    #     command = self.move_command(self.marseilles, self.burgundy)
    #     validator = get_command_validator(command)
    #     with self.assertRaises(ValidationError):
    #         validator.is_valid()

    # def test_cannot_move_to_complex_territory_and_not_named_coast(self):
    #     """
    #     A fleet cannot move to a complex territory without specifying which named
    #     coast.
    #     """
    #     self.set_piece_territory(self.fleet, self.mid_atlantic)
    #     command = self.move_command(
    #         self.mid_atlantic,
    #         self.spain,
    #     )
    #     validator = get_command_validator(command)
    #     with self.assertRaises(ValidationError):
    #         validator.is_valid()

    # def test_can_move_to_complex_territory_with_named_coast(self):
    #     """
    #     A fleet can move to a complex territory if specifying which named
    #     coast.
    #     """
    #     self.set_piece_territory(self.fleet, self.mid_atlantic)
    #     spain_nc = NamedCoast.objects.get(name='spain north coast')
    #     command = self.move_command(
    #         self.mid_atlantic,
    #         self.spain,
    #         target_coast=spain_nc
    #     )
    #     validator = get_command_validator(command)
    #     self.assertTrue(validator.is_valid())

    # def test_cannot_move_to_non_adjacent_named_coast(self):
    #     """
    #     A fleet cannot move to a named coast of a complex territory if the
    #     source territory is not a neighbour of the named coast.
    #     """
    #     self.set_piece_territory(self.fleet, self.western_mediterranean)
    #     spain_nc = NamedCoast.objects.get(name='spain north coast')
    #     command = self.move_command(
    #         self.western_mediterranean,
    #         self.spain,
    #         target_coast=spain_nc
    #     )
    #     validator = get_command_validator(command)
    #     with self.assertRaises(ValidationError):
    #         validator.is_valid()

    # def test_cannot_move_from_named_coast_to_non_neighbour(self):
    #     """
    #     A fleet cannot move from a named coast of a complex territory if the
    #     target territory is not a neighbour of the named coast.
    #     """
    #     spain_nc = NamedCoast.objects.get(name='spain north coast')
    #     self.set_piece_territory(self.fleet, self.spain, named_coast=spain_nc)
    #     command = self.move_command(
    #         self.spain,
    #         self.western_mediterranean,
    #         source_coast=spain_nc
    #     )
    #     validator = get_command_validator(command)
    #     with self.assertRaises(ValidationError):
    #         validator.is_valid()


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
        command = self.move_command(self.paris, self.burgundy)
        challenges = Challenge.objects.all()
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
        command = self.move_command(self.brest, self.english_channel)
        challenges = Challenge.objects.all()
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
