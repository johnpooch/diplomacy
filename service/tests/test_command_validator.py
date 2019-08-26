from django.core.exceptions import ValidationError


from service.command_validator import ArmyMoveValidator, FleetMoveValidator, \
    ArmySupportValidator, FleetSupportValidator, get_command_validator
from service.models import Command, NamedCoast, Nation, Order, Piece
from service.tests.base import HelperMixin, TerritoriesMixin
from .base import InitialGameStateTestCase as TestCase


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

    def test_get_army_support_validator(self):
        command = Command.objects.create(
            source_territory=self.paris,
            target_territory=self.burgundy,
            order=self.order,
            type=Command.CommandType.SUPPORT,
        )
        validator = get_command_validator(command)
        self.assertTrue(isinstance(validator, ArmySupportValidator))

    def test_get_fleet_support_validator(self):
        command = Command.objects.create(
            source_territory=self.brest,
            target_territory=self.english_channel,
            order=self.order,
            type=Command.CommandType.SUPPORT,
        )
        validator = get_command_validator(command)
        self.assertTrue(isinstance(validator, FleetSupportValidator))


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
        command = self.move_command(self.marseilles, self.piedmont)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_coastal_territory_no_shared_coast(self):
        """
        Army can move from coastal territory to adjacent coastal territory when
        no shared coast.
        """
        command = self.move_command(self.marseilles, self.gascony)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_inland_territory(self):
        """
        Army can move from coastal territory to adjacent inland territory.
        """
        command = self.move_command(self.marseilles, self.burgundy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_inland_to_adjacent_inland_territory(self):
        """
        Army can move from inland territory to adjacent inland territory.
        """
        command = self.move_command(self.paris, self.burgundy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_inland_to_adjacent_coastal_territory(self):
        """
        Army can move from inland territory to adjacent coastal territory.
        """
        command = self.move_command(self.paris, self.picardy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_coastal_to_adjacent_sea_territory(self):
        """
        Army cannot move from coastal to adjacent sea territory.
        """
        command = self.move_command(self.marseilles, self.gulf_of_lyon)
        validator = get_command_validator(command)
        with self.assertRaises(ValidationError):
            validator.is_valid()

    def test_coastal_to_non_adjacent_coastal_territory(self):
        """
        Army can move from a coastal territory to a non adjacent coastal
        territory via a convoy.
        """
        self.set_piece_territory(self.army, self.gascony)
        command = self.move_command(self.gascony, self.picardy)
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_inland_to_non_adjacent_inland_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent inland
        territory.
        """
        self.set_piece_territory(self.army, self.burgundy)
        command = self.move_command(self.burgundy, self.silesia)
        validator = get_command_validator(command)
        with self.assertRaises(ValidationError):
            validator.is_valid()

    def test_inland_to_non_adjacent_coastal_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent coastal
        territory.
        """
        self.set_piece_territory(self.army, self.silesia)
        command = self.move_command(self.silesia, self.gascony)
        validator = get_command_validator(command)
        with self.assertRaises(ValidationError):
            validator.is_valid()


class TestFleetSupportValidator(TestCase, TerritoriesMixin, HelperMixin):

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
        self.attacking_army = Piece.objects.get(territory__name='paris')
        self.attacking_fleet = Piece.objects.get(territory__name='london')

    def test_no_piece_in_source(self):
        """
        There must be a piece in the source territory.
        """
        # TODO repeat this test for move.
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support_command(
            self.belgium,
            self.kiel,
            self.holland
        )
        validator = get_command_validator(command)
        with self.assertRaisesRegexp(
            ValidationError,
            'No piece exists in this territory'
        ):
            validator.is_valid()

    def test_support_fleet_does_not_belong_to_command(self):
        """
        Supporting fleet must belong to nation which created the order.
        """
        self.set_piece_territory(self.attacking_fleet, self.belgium)
        command = self.support_command(
            self.kiel,
            self.belgium,
            self.holland
        )
        validator = get_command_validator(command)
        with self.assertRaisesRegexp(
            ValidationError,
            'No friendly piece exists in the source territory.'
        ):
            validator.is_valid()

    def test_support_fleet_to_adjacent_territory(self):
        """
        Fleet can support fleet to territory adjacent to both fleets.
        """
        self.set_piece_territory(self.attacking_fleet, self.english_channel)
        command = self.support_command(
            self.brest,
            self.picardy,
            self.english_channel
        )
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_support_fleet_to_territory_not_adjacent_to_supporting(self):
        """
        Fleet cannot support fleet to territory not adjacent to supporting
        fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support_command(
            self.brest,
            self.belgium,
            self.holland
        )
        validator = get_command_validator(command)
        with self.assertRaisesRegexp(
            ValidationError,
            'Supporting fleet cannot support piece into a territory which is '
            'not adjacent to the supporting fleet.'
        ):
            validator.is_valid()

    def test_support_fleet_to_territory_not_adjacent_to_attacking_fleet(self):
        """
        Supporting fleet cannot support fleet into territory which is not
        adjacent to the attacking fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support_command(
            self.brest,
            self.picardy,
            self.holland
        )
        validator = get_command_validator(command)
        with self.assertRaisesRegexp(
            ValidationError,
            'Supporting fleet cannot support fleet into territory which is '
            'not adjacent to the attacking fleet.'
        ):
            validator.is_valid()

    def test_support_army_to_territory_not_adjacent_to_attacking_army_coastal(self):
        """
        Supporting fleet can support army into territory which is not adjacent
        to the attacking army if convoy is possible.
        """
        self.set_piece_territory(self.attacking_army, self.wales)
        command = self.support_command(
            self.brest,
            self.picardy,
            self.wales
        )
        validator = get_command_validator(command)
        self.assertTrue(validator.is_valid())

    def test_support_army_to_territory_inland(self):
        """
        Supporting fleet cannot support army into inland territory.
        """
        self.set_piece_territory(self.attacking_army, self.picardy)
        command = self.support_command(
            self.brest,
            self.paris,
            self.picardy
        )
        validator = get_command_validator(command)
        with self.assertRaisesRegexp(
            ValidationError,
            'Target is not accessible by supporting piece.'
        ):
            validator.is_valid()

    def test_support_army_to_inland_territory(self):
        """
        Fleet cannot support army into an inland territory.
        """
        pass

    def test_support_from_named_coast_adjacent(self):
        """
        Fleet on a named coast can support army into a territory if the named
        coast is a neighbour of the territory.
        """
        pass

    def test_support_from_named_coast_not_adjacent(self):
        """
        Fleet on a named coast cannot support army into a territory if the
        named coast is not a neighbour of the territory.
        """
        pass

    def test_support_fleet_to_different_named_coast(self):
        """
        Fleet which neighbours one named coast of a complex territory (e.g.
        'Spain S.C') can support a fleet into the other named coast (e.g.
        'Spain N.C').
        """
        pass


class TestArmySupportValidator(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.army = Piece.objects.get(territory__name='paris')
        self.attacking_fleet = Piece.objects.get(territory__name='brest')
        self.attacking_army = Piece.objects.get(territory__name='marseilles')

    def test_support_fleet_to_territory_not_adjacent_to_supporting(self):
        """
        Supporting fleet must belong to nation which created the order.
        """
        pass

    def test_support_fleet_to_adjacent_territory_coastal(self):
        """
        Army can support fleet to territory adjacent to both pieces if coastal.
        """
        pass

    def test_support_fleet_to_adjacent_territory_sea(self):
        """
        Army cannot support fleet to territory adjacent to both pieces if
        territory is a sea territory.
        """
        pass

    def test_support_fleet_to_adjacent_territory_inland(self):
        """
        Army cannot support fleet to territory adjacent to both pieces if
        territory is inland.
        """
        pass

    def test_support_fleet_to_coastal_territory_not_adjacent_to_supporter(self):
        """
        Army cannot support fleet to coastal territory if not adjacent to
        supporting army.
        """
        pass

    def test_support_fleet_to_territory_not_adjacent_to_attacking_fleet(self):
        """
        Army cannot support fleet to territory not adjacent to attacking fleet.
        """
        pass

    def test_support_fleet_to_complex_territory_neighbour_named_coast(self):
        """
        An army can support a fleet into a complex territory when the army is
        adjacent to the named coast that the fleet is attacking.
        """
        pass

    def test_support_fleet_to_complex_territory_not_neighbour_named_coast(self):
        """
        An army can support a fleet into a complex territory when the army is
        adjacent to the territory but not adjacent to the named coast that the
        fleet is attacking.
        """
        pass
