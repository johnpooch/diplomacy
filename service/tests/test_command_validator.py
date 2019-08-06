from .base import InitialGameStateTestCase as TestCase

from service.command_validator import ArmyMoveValidator, FleetMoveValidator, \
    get_command_validator
from service.models import Command, NamedCoast, Nation, Order, Piece
from service.tests.base import TerritoriesMixin


class HelperMixin:

    def set_piece_territory(self, piece, territory, named_coast=None):
        """
        """
        piece.territory = territory
        piece.named_coast = named_coast
        piece.save()

    def create_move_command(self, source, target,
                            source_coast=None, target_coast=None):
        """
        """
        return Command.objects.create(
            source_territory=source,
            target_territory=target,
            order=self.order,
            type=Command.CommandType.MOVE,
            source_coast=source_coast,
            target_coast=target_coast,
        )


class TestGetCommandValidator(TestCase, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_get_army_move_validator(self):
        command = Command.objects.create(
            source_territory=self.paris,
            target_territory=self.burgundy,
            order=self.order,
            type=Command.CommandType.MOVE,
        )
        validator = get_command_validator(command)
        self.assertTrue(isinstance(validator, ArmyMoveValidator))

    def test_get_fleet_move_validator(self):
        command = Command.objects.create(
            source_territory=self.brest,
            target_territory=self.english_channel,
            order=self.order,
            type=Command.CommandType.MOVE,
        )
        validator = get_command_validator(command)
        self.assertTrue(isinstance(validator, FleetMoveValidator))


class TestFleetMoveValidator(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    # TODO bin validator messages

    # NOTE these tests should work without saving the object. Should instead do
    # ``command.validate()``. This is because the save function should run the
    # validate method and raise an error if the command is invalid.
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
        command = self.create_move_command(self.english_channel, self.irish_sea)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_sea_to_adjacent_coastal_territory(self):
        """
        Fleet can move from sea territory to adjacent coastal territory.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        command = self.create_move_command(self.english_channel, self.brest)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_coastal_territory_if_shared_coast(self):
        """
        Fleet can move from coastal territory to adjacent coastal territory.
        """
        self.set_piece_territory(self.fleet, self.brest)
        command = self.create_move_command(self.brest, self.gascony)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_coastal_territory_if_not_shared_coast(self):
        """
        Fleet cannot move from coastal territory to adjacent coastal territory
        when no shared coastline.
        """
        Piece.objects.get(territory__name='marseilles').delete()
        self.set_piece_territory(self.fleet, self.marseilles)
        command = self.create_move_command(self.marseilles, self.gascony)
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            ('Fleet cannot move from one coastal territory to another unless '
             'both territories share a coastline.')
        )

    def test_coastal_to_adjacent_inland_territory(self):
        """
        Fleet cannot move from coastal territory to adjacent inland territory.
        """
        Piece.objects.get(territory__name='marseilles').delete()
        self.set_piece_territory(self.fleet, self.marseilles)
        command = self.create_move_command(self.marseilles, self.burgundy)
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            'Target is not accessible by piece type.'
        )

    def test_cannot_move_to_complex_territory_and_not_named_coast(self):
        """
        A fleet cannot move to a complex territory without specifying which named
        coast.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        command = self.create_move_command(
            self.mid_atlantic,
            self.spain,
        )
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            ('Fleet cannot move to complex territory without specifying a '
             'named coast')
        )

    def test_can_move_to_complex_territory_with_named_coast(self):
        """
        A fleet can move to a complex territory if specifying which named
        coast.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        command = self.create_move_command(
            self.mid_atlantic,
            self.spain,
            target_coast=spain_nc
        )
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_cannot_move_to_non_adjacent_named_coast(self):
        """
        A fleet cannot move to a named coast of a complex territory if the
        source territory is not a neighbour of the named coast.
        """
        self.set_piece_territory(self.fleet, self.western_mediterranean)
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        command = self.create_move_command(
            self.western_mediterranean,
            self.spain,
            target_coast=spain_nc
        )
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            ('Fleet cannot move to a named coast which does not neighbour '
             'the source territory.')
        )

    def test_cannot_move_from_named_coast_to_non_neighbour(self):
        """
        A fleet cannot move from a named coast of a complex territory if the
        target territory is not a neighbour of the named coast.
        """
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        self.set_piece_territory(self.fleet, self.spain, named_coast=spain_nc)
        command = self.create_move_command(
            self.spain,
            self.western_mediterranean,
            source_coast=spain_nc
        )
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            ('Fleet cannot move from a named coast to a territory '
             'which is not a neighbour the named coast.')
        )


class TestArmyMoveValidator(TestCase, TerritoriesMixin, HelperMixin):

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
        command = self.create_move_command(self.marseilles, self.piedmont)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_coastal_territory_no_shared_coast(self):
        """
        Army can move from coastal territory to adjacent coastal territory when
        no shared coast.
        """
        command = self.create_move_command(self.marseilles, self.gascony)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_inland_territory(self):
        """
        Army can move from coastal territory to adjacent inland territory.
        """
        command = self.create_move_command(self.marseilles, self.burgundy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_inland_to_adjacent_inland_territory(self):
        """
        Army can move from inland territory to adjacent inland territory.
        """
        command = self.create_move_command(self.paris, self.burgundy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_inland_to_adjacent_coastal_territory(self):
        """
        Army can move from inland territory to adjacent coastal territory.
        """
        command = self.create_move_command(self.paris, self.picardy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_sea_territory(self):
        """
        Army cannot move from coastal to adjacent sea territory.
        """
        command = self.create_move_command(self.marseilles, self.gulf_of_lyon)
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            'Target is not accessible by piece type.'
        )

    def test_coastal_to_non_adjacent_coastal_territory(self):
        """
        Army can move from a coastal territory to a non adjacent coastal
        territory via a convoy.
        """
        self.set_piece_territory(self.army, self.gascony)
        command = self.create_move_command(self.gascony, self.picardy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_inland_to_non_adjacent_inland_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent inland
        territory.
        """
        self.set_piece_territory(self.army, self.burgundy)
        command = self.create_move_command(self.burgundy, self.silesia)
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            ('Army cannot move to non adjacent territory unless moving from '
             'one coastal territory to another coastal territory.')
        )

    def test_inland_to_non_adjacent_coastal_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent coastal
        territory.
        """
        self.set_piece_territory(self.army, self.silesia)
        command = self.create_move_command(self.silesia, self.gascony)
        validator = get_command_validator(command)
        self.assertFalse(validator.is_valid())
        self.assertEqual(
            validator.message,
            ('Army cannot move to non adjacent territory unless moving from '
             'one coastal territory to another coastal territory.')
        )
