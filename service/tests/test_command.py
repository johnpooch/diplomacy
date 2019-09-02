from django.core.exceptions import ValidationError

from service.command_validator import ArmyMoveValidator, FleetMoveValidator, \
    get_command_validator
from service.command_processor import Challenge, CommandProcessor
from service.models import Move, NamedCoast, Nation, Order, Piece
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


class TestFleetSupportClean(TestCase, TerritoriesMixin, HelperMixin):

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
        command = self.support(
            self.belgium,
            self.kiel,
            self.holland
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_fleet_does_not_belong_to_command(self):
        """
        Supporting fleet must belong to nation which created the order.
        """
        self.set_piece_territory(self.attacking_fleet, self.belgium)
        command = self.support(
            self.kiel,
            self.belgium,
            self.holland
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_fleet_to_adjacent_territory(self):
        """
        Fleet can support fleet to territory adjacent to both fleets.
        """
        self.set_piece_territory(self.attacking_fleet, self.english_channel)
        command = self.support(
            self.brest,
            self.picardy,
            self.english_channel
        )
        self.assertTrue(command.clean())

    def test_support_fleet_to_territory_not_adjacent_to_supporting(self):
        """
        Fleet cannot support fleet to territory not adjacent to supporting
        fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support(
            self.brest,
            self.belgium,
            self.holland
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_fleet_to_territory_not_adjacent_to_attacking_fleet(self):
        """
        Supporting fleet cannot support fleet into territory which is not
        adjacent to the attacking fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support(
            self.brest,
            self.picardy,
            self.holland
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_army_to_territory_not_adjacent_to_attacking_army_coastal(self):
        """
        Supporting fleet can support army into territory which is not adjacent
        to the attacking army if convoy is possible.
        """
        self.set_piece_territory(self.attacking_army, self.wales)
        command = self.support(
            self.brest,
            self.picardy,
            self.wales
        )
        self.assertTrue(command.clean())

    def test_support_army_to_territory_inland(self):
        """
        Supporting fleet cannot support army into inland territory.
        """
        self.set_piece_territory(self.attacking_army, self.picardy)
        command = self.support(
            self.brest,
            self.paris,
            self.picardy
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_from_named_coast_adjacent(self):
        """
        Fleet on a named coast can support army into a territory if the
        territory is a neighbour of the named coast.
        """
        spain_nc = NamedCoast.objects.get(name='spain north coast')
        self.set_piece_territory(self.fleet, self.spain, spain_nc)
        command = self.support(
            self.spain,
            self.gascony,
            self.marseilles,
        )
        self.assertTrue(command.clean())

    def test_support_from_named_coast_not_adjacent(self):
        """
        Fleet on a named coast cannot support army into a territory if the
        named coast is not a neighbour of the territory.
        """
        spain_sc = NamedCoast.objects.get(name='spain south coast')
        self.set_piece_territory(self.fleet, self.spain, spain_sc)
        command = self.support(
            self.spain,
            self.gascony,
            self.marseilles,
        )
        with self.assertRaises(ValidationError):
            self.assertTrue(command.clean())

    def test_support_fleet_to_different_named_coast(self):
        """
        Fleet which neighbours one named coast of a complex territory (e.g.
        'Spain S.C') can support a fleet into the other named coast (e.g.
        'Spain N.C').
        """
        self.set_piece_territory(self.fleet, self.gulf_of_lyon)
        self.set_piece_territory(self.attacking_fleet, self.mid_atlantic)
        command = self.support(
            self.gulf_of_lyon,
            self.spain,
            self.mid_atlantic,
        )
        self.assertTrue(command.clean())


class TestArmySupportClean(TestCase, TerritoriesMixin, HelperMixin):

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

    def test_support_fleet_to_adjacent_territory_coastal(self):
        """
        Army can support fleet to territory adjacent to both pieces if coastal.
        """
        self.set_piece_territory(self.attacking_fleet, self.gulf_of_lyon)
        command = self.support(
            self.marseilles,
            self.piedmont,
            self.gulf_of_lyon
        )
        self.assertTrue(command.clean())

    def test_support_fleet_to_adjacent_territory_sea(self):
        """
        Army cannot support fleet to sea territory.
        """
        self.set_piece_territory(self.attacking_fleet, self.piedmont)
        command = self.support(
            self.marseilles,
            self.gulf_of_lyon,
            self.piedmont
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_fleet_to_adjacent_territory_inland(self):
        """
        Army cannot support fleet to territory adjacent to both pieces if
        territory is inland.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.support(
            self.marseilles,
            self.burgundy,
            self.gascony
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_fleet_to_coastal_territory_not_adjacent_to_supporter(self):
        """
        Army cannot support fleet to coastal territory if not adjacent to
        supporting army.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.support(
            self.marseilles,
            self.paris,
            self.gascony
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_fleet_to_territory_not_adjacent_to_attacking_fleet(self):
        """
        Army cannot support fleet to territory not adjacent to attacking fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.support(
            self.marseilles,
            self.piedmont,
            self.gascony
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_support_fleet_to_complex_territory_neighbour_named_coast(self):
        """
        An army can support a fleet into a complex territory when the army is
        adjacent to the named coast that the fleet is attacking.
        """
        self.set_piece_territory(self.army, self.gascony)
        self.set_piece_territory(self.attacking_fleet, self.mid_atlantic)
        command = self.support(
            self.gascony,
            self.spain,
            self.mid_atlantic
        )
        self.assertTrue(command.clean())

    def test_support_fleet_to_complex_territory_not_neighbour_named_coast(self):
        """
        An army can support a fleet into a complex territory when the army is
        adjacent to the territory but not adjacent to the named coast that the
        fleet is attacking.
        """
        self.set_piece_territory(self.army, self.gascony)
        self.set_piece_territory(self.attacking_fleet, self.mid_atlantic)
        command = self.support(
            self.marseilles,
            self.spain,
            self.mid_atlantic
        )
        self.assertTrue(command.clean())


class TestFleetConvoyClean(TestCase, TerritoriesMixin, HelperMixin):

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
        self.attacking_fleet = Piece.objects.get(territory__name='brest')
        self.attacking_army = Piece.objects.get(territory__name='paris')

    def test_convoy_fleet(self):
        """
        Cannot convoy fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.convoy(
            self.brest,
            self.picardy,
            self.gascony
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_convoy_army(self):
        """
        Can convoy army if army is on the coast, target is coastal, and fleet is
        at sea.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        self.set_piece_territory(self.attacking_army, self.wales)
        command = self.convoy(
            self.english_channel,
            self.picardy,
            self.wales
        )
        self.assertTrue(command.clean())

    def test_convoy_army_fleet_on_coast(self):
        """
        Cannot convoy army if fleet is on land.
        """
        self.set_piece_territory(self.attacking_army, self.gascony)
        command = self.convoy(
            self.brest,
            self.picardy,
            self.gascony
        )
        with self.assertRaises(ValidationError):
            self.assertTrue(command.clean())

    def test_convoy_army_from_complex_territory(self):
        """
        Can convoy army from complex territory.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        self.set_piece_territory(self.attacking_army, self.spain)
        command = self.convoy(
            self.mid_atlantic,
            self.brest,
            self.spain
        )
        self.assertTrue(command.clean())

    def test_convoy_army_to_complex_territory(self):
        """
        Can convoy army to complex territory.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        self.set_piece_territory(self.attacking_army, self.brest)
        command = self.convoy(
            self.mid_atlantic,
            self.spain,
            self.brest
        )
        self.assertTrue(command.clean())

    def test_convoy_army_from_complex_territory_to_complex_territory(self):
        """
        Can convoy army from complex territory to another complex territory.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        self.set_piece_territory(self.attacking_army, self.st_petersburg)
        command = self.convoy(
            self.mid_atlantic,
            self.spain,
            self.st_petersburg
        )
        self.assertTrue(command.clean())


class TestBuildClean(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json', 'supply_centers.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = Piece.objects.get(territory__name='brest')
        self.attacking_fleet = Piece.objects.get(territory__name='brest')
        self.attacking_army = Piece.objects.get(territory__name='paris')

    def test_build_army_supply_center_not_in_national_borders(self):
        """
        Cannot build army in territory with a supply center which is not in
        national borders.
        """
        command = self.build(
            self.london,
            Piece.PieceType.FLEET
        )
        with self.assertRaises(ValidationError):
            self.assertTrue(command.clean())

    def test_build_army_supply_center_not_controlled_by_nation(self):
        """
        Cannot build army in territory with a supply center which is within
        national borders but not controlled by nation.
        """
        self.paris.controlled_by = Nation.objects.get(name='England')
        self.paris.save()
        command = self.build(
            self.paris,
            Piece.PieceType.ARMY
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_build_army_no_supply_center(self):
        """
        Cannot build army in territory with no supply center.
        """
        command = self.build(
            self.burgundy,
            Piece.PieceType.ARMY
        )
        with self.assertRaises(ValidationError):
            command.clean()

    def test_build_army_coastal(self):
        """
        Can build army on coastal territory with supply center.
        """
        Piece.objects.get(territory=self.brest).delete()
        command = self.build(
            self.brest,
            Piece.PieceType.ARMY
        )
        self.assertTrue(command.clean())

    def test_build_army_inland(self):
        """
        Can build army on inland territory with supply center.
        """
        Piece.objects.get(territory=self.paris).delete()
        command = self.build(
            self.paris,
            Piece.PieceType.ARMY
        )
        self.assertTrue(command.clean())

    def test_build_fleet_coastal(self):
        """
        Can build fleet on coastal territory with supply center.
        """
        Piece.objects.get(territory=self.brest).delete()
        command = self.build(
            self.brest,
            Piece.PieceType.FLEET
        )
        self.assertTrue(command.clean())

    def test_build_fleet_inland(self):
        """
        Cannot build fleet on inland territory with supply center.
        """
        Piece.objects.get(territory=self.paris).delete()
        command = self.build(
            self.paris,
            Piece.PieceType.FLEET
        )
        with self.assertRaises(ValidationError):
            command.clean()
