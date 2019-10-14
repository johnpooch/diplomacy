from core import models
from core.models.base import CommandState, CommandType, PieceType
from core.tests.base import HelperMixin, TerritoriesMixin
from .base import InitialGameStateTestCase as TestCase


class TestFleetMoveClean(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = models.Piece.objects.get(territory__name='brest')

    def test_sea_to_adjacent_sea_territory(self):
        """
        Fleet can move to adjacent sea territory.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        command = self.move(self.fleet, self.english_channel, self.irish_sea)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_sea_to_adjacent_coastal_territory(self):
        """
        Fleet can move from sea territory to adjacent coastal territory.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        command = self.move(self.fleet, self.english_channel, self.brest)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_coastal_to_adjacent_coastal_territory_if_shared_coast(self):
        """
        Fleet can move from coastal territory to adjacent coastal territory.
        """
        self.set_piece_territory(self.fleet, self.brest)
        command = self.move(self.fleet, self.brest, self.gascony)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_coastal_to_adjacent_coastal_territory_if_not_shared_coast(self):
        """
        Fleet cannot move from coastal territory to adjacent coastal territory
        when no shared coastline.
        """
        models.Piece.objects.get(territory__name='marseilles').delete()
        self.set_piece_territory(self.fleet, self.marseilles)
        command = self.move(self.fleet, self.marseilles, self.gascony)
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_coastal_to_adjacent_inland_territory(self):
        """
        Fleet cannot move from coastal territory to adjacent inland territory.
        """
        models.Piece.objects.get(territory__name='marseilles').delete()
        self.set_piece_territory(self.fleet, self.marseilles)
        command = self.move(self.fleet, self.marseilles, self.burgundy)
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_cannot_move_to_complex_territory_and_not_named_coast(self):
        """
        A fleet cannot move to a complex territory without specifying which
        named coast.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        command = self.move(self.fleet, self.mid_atlantic, self.spain)
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_can_move_to_complex_territory_with_named_coast(self):
        """
        A fleet can move to a complex territory if specifying which named
        coast.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        spain_nc = models.NamedCoast.objects.get(name='spain north coast')
        command = self.move(
            self.fleet,
            self.mid_atlantic,
            self.spain,
            target_coast=spain_nc
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_cannot_move_to_non_adjacent_named_coast(self):
        """
        A fleet cannot move to a named coast of a complex territory if the
        source territory is not a neighbour of the named coast.
        """
        self.set_piece_territory(self.fleet, self.western_mediterranean)
        spain_nc = models.NamedCoast.objects.get(name='spain north coast')
        command = self.move(
            self.fleet,
            self.western_mediterranean,
            self.spain,
            target_coast=spain_nc
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_cannot_move_from_named_coast_to_non_neighbour(self):
        """
        A fleet cannot move from a named coast of a complex territory if the
        target territory is not a neighbour of the named coast.
        """
        spain_nc = models.NamedCoast.objects.get(name='spain north coast')
        self.set_piece_territory(self.fleet, self.spain, named_coast=spain_nc)
        command = self.move(
            self.fleet,
            self.spain,
            self.western_mediterranean,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)


class TestArmyMoveClean(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.army = models.Piece.objects.get(territory__name='marseilles')

    def test_coastal_to_adjacent_coastal_territory_shared_coast(self):
        """
        Army can move from a coastal territory to an adjacent coastal territory
        when there is a shared coast.
        """
        command = self.move(self.army, self.marseilles, self.piedmont)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_coastal_to_adjacent_coastal_territory_no_shared_coast(self):
        """
        Army can move from coastal territory to adjacent coastal territory when
        no shared coast.
        """
        command = self.move(self.army, self.marseilles, self.gascony)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_coastal_to_adjacent_inland_territory(self):
        """
        Army can move from coastal territory to adjacent inland territory.
        """
        command = self.move(self.army, self.marseilles, self.burgundy)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_inland_to_adjacent_inland_territory(self):
        """
        Army can move from inland territory to adjacent inland territory.
        """
        self.army = models.Piece.objects.get(territory=self.paris)
        command = self.move(self.army, self.paris, self.burgundy)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_inland_to_adjacent_coastal_territory(self):
        """
        Army can move from inland territory to adjacent coastal territory.
        """
        self.army = models.Piece.objects.get(territory=self.paris)
        command = self.move(self.army, self.paris, self.picardy)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_coastal_to_adjacent_sea_territory(self):
        """
        Army cannot move from coastal to adjacent sea territory.
        """
        command = self.move(self.army, self.marseilles, self.gulf_of_lyon)
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_coastal_to_non_adjacent_coastal_territory(self):
        """
        Army can move from a coastal territory to a non adjacent coastal
        territory via a convoy.
        """
        self.set_piece_territory(self.army, self.gascony)
        command = self.move(self.army, self.gascony, self.picardy)
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_inland_to_non_adjacent_inland_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent inland
        territory.
        """
        self.set_piece_territory(self.army, self.burgundy)
        command = self.move(self.army, self.burgundy, self.silesia)
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_inland_to_non_adjacent_coastal_territory(self):
        """
        Army cannot move from an inland territory to a non adjacent coastal
        territory.
        """
        self.set_piece_territory(self.army, self.silesia)
        command = self.move(self.army, self.silesia, self.gascony)
        command.check_illegal()
        self.assertTrue(command.illegal)


class TestFleetSupportClean(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = models.Piece.objects.get(territory__name='brest')
        self.attacking_army = models.Piece.objects.get(territory__name='paris')
        self.attacking_fleet = models.Piece.objects.get(territory__name='london')

    def test_no_piece_in_source(self):
        """
        There must be a piece in the source territory.
        """
        # TODO repeat this test for move.
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support(
            self.fleet,
            self.belgium,
            self.kiel,
            self.holland
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_does_not_belong_to_command(self):
        """
        Supporting fleet must belong to nation which created the order.
        """
        self.set_piece_territory(self.attacking_fleet, self.belgium)
        command = self.support(
            self.fleet,
            self.kiel,
            self.belgium,
            self.holland,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_to_adjacent_territory(self):
        """
        Fleet can support fleet to territory adjacent to both fleets.
        """
        self.set_piece_territory(self.attacking_fleet, self.english_channel)
        command = self.support(
            self.fleet,
            self.brest,
            self.english_channel,
            self.picardy,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_support_fleet_to_territory_not_adjacent_to_supporting(self):
        """
        Fleet cannot support fleet to territory not adjacent to supporting
        fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support(
            self.fleet,
            self.brest,
            self.belgium,
            self.holland
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_to_territory_not_adjacent_to_attacking_fleet(self):
        """
        Supporting fleet cannot support fleet into territory which is not
        adjacent to the attacking fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.holland)
        command = self.support(
            self.fleet,
            self.brest,
            self.holland,
            self.picardy,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_army_to_territory_not_adjacent_to_attacking_army_coastal(self):
        """
        Supporting fleet can support army into territory which is not adjacent
        to the attacking army if convoy is possible.
        """
        self.set_piece_territory(self.attacking_army, self.wales)
        command = self.support(
            self.fleet,
            self.brest,
            self.wales,
            self.picardy,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_support_army_to_territory_inland(self):
        """
        Supporting fleet cannot support army into inland territory.
        """
        self.set_piece_territory(self.attacking_army, self.picardy)
        command = self.support(
            self.fleet,
            self.brest,
            self.paris,
            self.picardy
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_from_named_coast_adjacent(self):
        """
        Fleet on a named coast can support army into a territory if the
        territory is a neighbour of the named coast.
        """
        spain_nc = models.NamedCoast.objects.get(name='spain north coast')
        self.set_piece_territory(self.fleet, self.spain, spain_nc)
        command = self.support(
            self.fleet,
            self.spain,
            self.marseilles,
            self.gascony,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_support_from_named_coast_not_adjacent(self):
        """
        Fleet on a named coast cannot support army into a territory if the
        named coast is not a neighbour of the territory.
        """
        spain_sc = models.NamedCoast.objects.get(name='spain south coast')
        self.set_piece_territory(self.fleet, self.spain, spain_sc)
        command = self.support(
            self.fleet,
            self.spain,
            self.gascony,
            self.marseilles,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_to_different_named_coast(self):
        """
        Fleet which neighbours one named coast of a complex territory (e.g.
        'Spain S.C') can support a fleet into the other named coast (e.g.
        'Spain N.C').
        """
        self.set_piece_territory(self.fleet, self.gulf_of_lyon)
        self.set_piece_territory(self.attacking_fleet, self.mid_atlantic)
        command = self.support(
            self.fleet,
            self.gulf_of_lyon,
            self.mid_atlantic,
            self.spain,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)


class TestArmySupportClean(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.army = models.Piece.objects.get(territory__name='paris')
        self.attacking_fleet = models.Piece.objects.get(territory__name='brest')
        self.attacking_army = models.Piece.objects.get(territory__name='marseilles')

    def test_support_fleet_to_adjacent_territory_coastal(self):
        """
        Army can support fleet to territory adjacent to both pieces if coastal.
        """
        self.set_piece_territory(self.attacking_fleet, self.gulf_of_lyon)
        command = self.support(
            self.army,
            self.marseilles,
            self.gulf_of_lyon,
            self.piedmont,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_support_fleet_to_adjacent_territory_sea(self):
        """
        Army cannot support fleet to sea territory.
        """
        self.set_piece_territory(self.attacking_fleet, self.piedmont)
        command = self.support(
            self.army,
            self.marseilles,
            self.piedmont,
            self.gulf_of_lyon,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_to_adjacent_territory_inland(self):
        """
        Army cannot support fleet to territory adjacent to both pieces if
        territory is inland.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.support(
            self.army,
            self.marseilles,
            self.gascony,
            self.burgundy,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_to_coastal_territory_not_adjacent_to_supporter(self):
        """
        Army cannot support fleet to coastal territory if not adjacent to
        supporting army.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.support(
            self.army,
            self.marseilles,
            self.gascony,
            self.paris,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_to_territory_not_adjacent_to_attacking_fleet(self):
        """
        Army cannot support fleet to territory not adjacent to attacking fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.support(
            self.army,
            self.marseilles,
            self.gascony,
            self.piedmont,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_support_fleet_to_complex_territory_neighbour_named_coast(self):
        """
        An army can support a fleet into a complex territory when the army is
        adjacent to the named coast that the fleet is attacking.
        """
        self.set_piece_territory(self.army, self.gascony)
        self.set_piece_territory(self.attacking_fleet, self.mid_atlantic)
        command = self.support(
            self.army,
            self.gascony,
            self.mid_atlantic,
            self.spain,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_support_fleet_to_complex_territory_not_neighbour_named_coast(self):
        """
        An army can support a fleet into a complex territory when the army is
        adjacent to the territory but not adjacent to the named coast that the
        fleet is attacking.
        """
        self.set_piece_territory(self.army, self.gascony)
        self.set_piece_territory(self.attacking_fleet, self.mid_atlantic)
        command = self.support(
            self.army,
            self.marseilles,
            self.mid_atlantic,
            self.spain,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)


class TestFleetConvoyClean(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = models.Piece.objects.get(territory__name='brest')
        self.attacking_fleet = models.Piece.objects.get(territory__name='brest')
        self.attacking_army = models.Piece.objects.get(territory__name='paris')

    def test_convoy_fleet(self):
        """
        Cannot convoy fleet.
        """
        self.set_piece_territory(self.attacking_fleet, self.gascony)
        command = self.convoy(
            self.fleet,
            self.brest,
            self.picardy,
            self.gascony
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_convoy_army(self):
        """
        Can convoy army if army is on the coast, target is coastal, and fleet is
        at sea.
        """
        self.set_piece_territory(self.fleet, self.english_channel)
        self.set_piece_territory(self.attacking_army, self.wales)
        command = self.convoy(
            self.fleet,
            self.english_channel,
            self.picardy,
            self.wales
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_convoy_army_fleet_on_coast(self):
        """
        Cannot convoy army if fleet is on land.
        """
        self.set_piece_territory(self.attacking_army, self.gascony)
        command = self.convoy(
            self.fleet,
            self.brest,
            self.picardy,
            self.gascony
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_convoy_army_from_complex_territory(self):
        """
        Can convoy army from complex territory.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        self.set_piece_territory(self.attacking_army, self.spain)
        command = self.convoy(
            self.fleet,
            self.mid_atlantic,
            self.brest,
            self.spain
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_convoy_army_to_complex_territory(self):
        """
        Can convoy army to complex territory.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        self.set_piece_territory(self.attacking_army, self.brest)
        command = self.convoy(
            self.fleet,
            self.mid_atlantic,
            self.spain,
            self.brest
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_convoy_army_from_complex_territory_to_complex_territory(self):
        """
        Can convoy army from complex territory to another complex territory.
        """
        self.set_piece_territory(self.fleet, self.mid_atlantic)
        self.set_piece_territory(self.attacking_army, self.st_petersburg)
        command = self.convoy(
            self.fleet,
            self.mid_atlantic,
            self.spain,
            self.st_petersburg
        )
        command.check_illegal()
        self.assertFalse(command.illegal)


class TestBuildClean(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json', 'supply_centers.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = models.Piece.objects.get(territory__name='brest')
        self.attacking_fleet = models.Piece.objects.get(territory__name='brest')
        self.attacking_army = models.Piece.objects.get(territory__name='paris')

    def test_build_army_supply_center_not_in_national_borders(self):
        """
        Cannot build army in territory with a supply center which is not in
        national borders.
        """
        command = self.build(
            self.london,
            PieceType.FLEET
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_build_army_supply_center_not_controlled_by_nation(self):
        """
        Cannot build army in territory with a supply center which is within
        national borders but not controlled by nation.
        """
        self.paris.controlled_by = models.Nation.objects.get(name='England')
        self.paris.save()
        command = self.build(
            self.paris,
            PieceType.ARMY
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_build_army_no_supply_center(self):
        """
        Cannot build army in territory with no supply center.
        """
        command = self.build(
            self.burgundy,
            PieceType.ARMY
        )
        command.check_illegal()
        self.assertTrue(command.illegal)

    def test_build_army_coastal(self):
        """
        Can build army on coastal territory with supply center.
        """
        models.Piece.objects.get(territory=self.brest).delete()
        command = self.build(
            self.brest,
            PieceType.ARMY,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_build_army_inland(self):
        """
        Can build army on inland territory with supply center.
        """
        models.Piece.objects.get(territory=self.paris).delete()
        command = self.build(
            self.paris,
            PieceType.ARMY,
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_build_fleet_coastal(self):
        """
        Can build fleet on coastal territory with supply center.
        """
        models.Piece.objects.get(territory=self.brest).delete()
        command = self.build(
            self.brest,
            PieceType.FLEET
        )
        command.check_illegal()
        self.assertFalse(command.illegal)

    def test_build_fleet_inland(self):
        """
        Cannot build fleet on inland territory with supply center.
        """
        models.Piece.objects.get(territory=self.paris).delete()
        command = self.build(
            self.paris,
            PieceType.FLEET
        )
        command.check_illegal()
        self.assertTrue(command.illegal)


class TestSupportCut(TestCase, TerritoriesMixin, HelperMixin):
    """
    """
    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json', 'supply_centers.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = models.Order.objects.create(
            nation=models.Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = models.Piece.objects.get(territory__name='brest')
        self.attacking_fleet = models.Piece.objects.get(territory__name='brest')
        self.supporting_army = models.Piece.objects.get(territory__name='paris')

    def test_no_other_unit_is_ordered_to_move_to_supporting_territory(self):
        """
        If no other piece is ordered to move to the territory where the
        supporting unit is positioned, the supporting command is not cut.
        """
        support_command = self.support(
            self.supporting_army,
            self.paris,
            self.brest,
            self.picardy,
        )
        support_command.save()
        self.assertFalse(support_command.cut)

    def test_non_support_command_raises_value_error(self):
        """
        All command types other than support cannot use ``cut()`` method. A
        ``ValueError`` is raised if this method is accessed by a non-support
        command.
        """
        move_command = models.Command(
            source=self.paris,
            piece=self.supporting_army,
            aux=self.brest,
            target=self.picardy,
            type=CommandType.MOVE,
            order=self.order
        )
        with self.assertRaises(ValueError):
            move_command.cut

    def test_foreign_attacking_piece(self):
        """
        If there is a foreign piece moving into the territory of the supoorting
        piece and the attacking piece is not coming from the target of the
        supported piece, the support is cut.
        """
        pass

    def test_foreign_attacking_piece_from_support_target(self):
        """
        If there is a foreign piece moving into the territory of the supoorting
        piece but the attacking piece is coming from the target of the
        supported piece, the support is not cut.
        """
        pass


class TestGetConvoyPaths(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.france = models.Nation.objects.get(name='France')
        self.order = models.Order.objects.create(
            nation=self.france,
            turn=self.turn,
        )
        self.army = models.Piece.objects.get(territory__name='paris')
        self.convoying_fleet = models.Piece.objects.get(territory__name='brest')
        self.set_piece_territory(self.convoying_fleet, self.english_channel)
        self.set_piece_territory(self.army, self.belgium)

    def test_no_convoy_no_path_returned(self):
        """
        If there is no convoying fleets an empty list is returned.
        """
        convoy_paths = models.Command.objects.get_convoy_paths(
            self.belgium,
            self.london
        )
        self.assertEqual(len(convoy_paths), 0)

    def test_single_territory_convoy_is_added(self):
        """
        If there is a single fleet convoying from source to target and that
        fleet is a neighbour of both the source and the target, the returned
        list should contain a tuple with only that fleet's command.
        """
        convoy_command = models.Command.objects.create(
            source=self.english_channel,
            piece=self.convoying_fleet,
            aux=self.belgium,
            target=self.london,
            type=CommandType.CONVOY,
            order=self.order
        )
        convoy_paths = models.Command.objects.get_convoy_paths(
            self.belgium,
            self.london
        )
        # length of set is 1
        self.assertEqual(len(convoy_paths), 1)
        # length of tuple is 1
        self.assertEqual(len(convoy_paths[0]), 1)
        # tuple item is convoy command
        self.assertEqual(convoy_paths[0][0], convoy_command)

    def test_two_territories_can_convoy(self):
        """
        If there are two territories that can convoy from source to target
        directly, a list is returned with two tuples, each containing only one
        command.
        """
        north_sea_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.north_sea,
            type=PieceType.FLEET
        )
        english_channel_command = models.Command.objects.create(
            source=self.english_channel,
            piece=self.convoying_fleet,
            aux=self.belgium,
            target=self.london,
            type=CommandType.CONVOY,
            order=self.order
        )
        north_sea_command = models.Command.objects.create(
            source=self.north_sea,
            piece=north_sea_fleet,
            aux=self.belgium,
            target=self.london,
            type=CommandType.CONVOY,
            order=self.order
        )
        convoy_paths = models.Command.objects.get_convoy_paths(
            self.belgium,
            self.london
        )
        self.assertEqual(len(convoy_paths), 2)
        self.assertTrue(english_channel_command in
                        [convoy_paths[0][0], convoy_paths[1][0]])
        self.assertTrue(north_sea_command in
                        [convoy_paths[0][0], convoy_paths[1][0]])

    def test_single_path_with_two_territories(self):
        """
        If there are two covoying commands which make a convoy chain from
        target to source, a list with a single tuple containing both commands
        is returned.
        """
        self.set_piece_territory(self.army, self.picardy)
        north_sea_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.north_sea,
            type=PieceType.FLEET
        )
        english_channel_command = models.Command.objects.create(
            source=self.english_channel,
            piece=self.convoying_fleet,
            aux=self.picardy,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        north_sea_command = models.Command.objects.create(
            source=self.north_sea,
            piece=north_sea_fleet,
            aux=self.picardy,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        convoy_paths = models.Command.objects.get_convoy_paths(
            self.picardy,
            self.edinburgh
        )
        self.assertEqual(len(convoy_paths), 1)
        self.assertTrue(english_channel_command in
                        [convoy_paths[0][0], convoy_paths[0][1]])
        self.assertTrue(north_sea_command in
                        [convoy_paths[0][0], convoy_paths[0][1]])

    def test_single_path_with_three_territories(self):
        """
        If there are three covoying commands which make a convoy chain from
        target to source, a list with a single tuple containing all three
        commands is returned.
        """
        self.set_piece_territory(self.army, self.portugal)
        north_sea_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.north_sea,
            type=PieceType.FLEET
        )
        mid_atlantic_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.mid_atlantic,
            type=PieceType.FLEET
        )
        english_channel_command = models.Command.objects.create(
            source=self.english_channel,
            piece=self.convoying_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        north_sea_command = models.Command.objects.create(
            source=self.north_sea,
            piece=north_sea_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        mid_atlantic_command = models.Command.objects.create(
            source=self.mid_atlantic,
            piece=mid_atlantic_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        convoy_paths = models.Command.objects.get_convoy_paths(
            self.portugal,
            self.edinburgh
        )
        self.assertEqual(len(convoy_paths), 1)
        self.assertEqual(len(convoy_paths[0]), 3)
        self.assertTrue(
            english_channel_command in
            [convoy_paths[0][0], convoy_paths[0][1], convoy_paths[0][2]]
        )
        self.assertTrue(
            north_sea_command in
            [convoy_paths[0][0], convoy_paths[0][1], convoy_paths[0][2]]
        )
        self.assertTrue(
            mid_atlantic_command in
            [convoy_paths[0][0], convoy_paths[0][1], convoy_paths[0][2]]
        )

    def test_multiple_paths_with_multiple_territories(self):
        """
        If there are multiple routes in a set of convoying commands, those
        routes are returned.
        """
        self.set_piece_territory(self.army, self.portugal)
        north_sea_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.north_sea,
            type=PieceType.FLEET
        )
        mid_atlantic_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.mid_atlantic,
            type=PieceType.FLEET
        )
        north_atlantic_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.north_atlantic,
            type=PieceType.FLEET
        )
        norwegian_sea_fleet = models.Piece.objects.create(
            nation=self.france,
            territory=self.norwegian_sea,
            type=PieceType.FLEET
        )
        english_channel_command = models.Command.objects.create(
            source=self.english_channel,
            piece=self.convoying_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        north_sea_command = models.Command.objects.create(
            source=self.north_sea,
            piece=north_sea_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        mid_atlantic_command = models.Command.objects.create(
            source=self.mid_atlantic,
            piece=mid_atlantic_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        north_atlantic_command = models.Command.objects.create(
            source=self.north_atlantic,
            piece=north_atlantic_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        norwegian_sea_command = models.Command.objects.create(
            source=self.norwegian_sea,
            piece=norwegian_sea_fleet,
            aux=self.portugal,
            target=self.edinburgh,
            type=CommandType.CONVOY,
            order=self.order
        )
        path_a = (mid_atlantic_command, north_atlantic_command,
                  norwegian_sea_command)
        path_b = (mid_atlantic_command, english_channel_command,
                  north_sea_command)
        convoy_paths = models.Command.objects.get_convoy_paths(
            self.portugal,
            self.edinburgh
        )
        self.assertEqual(len(convoy_paths), 2)
        self.assertEqual(path_a, convoy_paths[0])
        self.assertEqual(path_b, convoy_paths[1])


class TestMovePath(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.france = models.Nation.objects.get(name='France')
        self.germany = models.Nation.objects.get(name='Germany')
        self.order = models.Order.objects.create(
            nation=self.france,
            turn=self.turn,
        )
        self.german_order = models.Order.objects.create(
            nation=self.germany,
            turn=self.turn,
        )
        self.army = models.Piece.objects.get(territory__name='paris')
        self.fleet = models.Piece.objects.get(territory__name='brest')

    def test_army_move_to_adjacent_land_territory(self):
        """
        ``move_path`` will be ``True`` if an army is moving to an adjacent land
        territory.
        """
        move = self.move(self.army, self.paris, self.burgundy)
        self.assertTrue(move.move_path)

    def test_army_move_to_adjacent_sea_territory(self):
        """
        ``move_path`` will be ``False`` if an army is moving to an adjacent
        sea territory.
        """
        self.set_piece_territory(self.army, self.picardy)
        move = self.move(self.army, self.picardy, self.english_channel)
        self.assertFalse(move.move_path)

    def test_army_move_to_non_adjacent_inland_territory(self):
        """
        ``move_path`` will be ``False`` if an army is moving to a non adjacent
        inland territory.
        """
        move = self.move(self.army, self.paris, self.munich)
        self.assertFalse(move.move_path)

    def test_army_move_to_non_adjacent_coastal_territory_no_convoy(self):
        """
        ``move_path`` will be ``False`` if an army is moving to a non adjacent
        coastal territory and there is no convoy.
        """
        self.set_piece_territory(self.army, self.picardy)
        move = self.move(self.army, self.picardy, self.london)
        self.assertFalse(move.move_path)

    def test_army_move_to_non_adjacent_coastal_territory_unsuccessful_convoy(self):
        """
        ``move_path`` will be ``False`` if an army is moving to a non adjacent
        coastal territory and there is a convoy but it is not successful.
        """
        self.set_piece_territory(self.army, self.picardy)
        move = self.move(self.army, self.picardy, self.london)
        self.set_piece_territory(self.fleet, self.english_channel)
        self.convoy(
            self.fleet,
            self.english_channel,
            self.london,
            self.picardy
        ).save()

        germany = models.Nation.objects.get(name='Germany')

        # attacking piece
        models.Piece.objects.create(
            nation=germany,
            territory=self.north_sea,
            type=PieceType.FLEET,
        )
        models.Command.objects.create(
            piece=self.army,
            source=self.north_sea,
            target=self.english_channel,
            type=CommandType.MOVE,
            order=self.german_order,
        ).save()

        # supporting piece
        supporting_piece = models.Piece.objects.create(
            nation=germany,
            territory=self.irish_sea,
            type=PieceType.FLEET,
        )
        models.Command.objects.create(
            piece=supporting_piece,
            source=self.irish_sea,
            target=self.english_channel,
            aux=self.north_sea,
            type=CommandType.SUPPORT,
            order=self.german_order,
        )
        self.assertFalse(move.move_path)

    def test_army_move_to_non_adjacent_coastal_territory_successful_convoy(self):
        """
        ``move_path`` will be ``True`` if an army is moving to a non adjacent
        coastal territory and there is a successful convoy.
        """
        self.set_piece_territory(self.army, self.picardy)
        self.set_piece_territory(self.fleet, self.english_channel)
        move = self.move(self.army, self.picardy, self.london)
        self.convoy(
            self.fleet,
            self.english_channel,
            self.london,
            self.picardy,
        ).save()
        self.assertTrue(move.move_path)

    def test_fleet_move_to_adjacent_coastal_territory(self):
        """
        ``move_path`` will be ``True`` if a fleet is moving to an adjacent
        coastal territory.
        """
        pass

    def test_fleet_move_to_adjacent_sea_territory(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        sea territory.
        """
        pass

    def test_fleet_move_to_adjacent_inland_territory(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass

    def test_fleet_move_from_named_coast_to_adjacent_sea_territory(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass

    def test_fleet_move_from_named_coast_to_adjacent_coastal_territory(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass

    def test_fleet_move_from_named_coast_to_non_adjacent_sea_territory(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass

    def test_fleet_move_from_sea_territory_to_adjarent_named_coast(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass

    def test_fleet_move_from_sea_territory_to_non_adjacent_named_coast(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass

    def test_fleet_move_from_coastal_territory_to_adjacent_named_coast(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass

    def test_fleet_move_from_coastal_territory_to_non_adjacent_named_coast(self):
        """
        ``move_path`` will be ``False`` if a fleet is moving to an adjacent
        inland territory.
        """
        pass


class TestResolveMove(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.france = models.Nation.objects.get(name='France')
        self.order = models.Order.objects.create(
            nation=self.france,
            turn=self.turn,
        )
        germany = models.Nation.objects.get(name='Germany')
        self.german_order = models.Order.objects.create(
            nation=germany,
            turn=self.turn,
        )
        self.army = models.Piece.objects.get(territory__name='paris')
        self.german_army = models.Piece.objects.get(territory__name='munich')

    def test_move_to_unoccupied_and_unchallenged_area(self):
        """
        A move to an unoccupied territory where there are no attacking pieces
        succeeds.
        """
        move = self.move(self.army, self.paris, self.gascony)
        self.assertTrue(move.unresolved)
        move.resolve()
        self.assertTrue(move.succeeds)

    def test_move_to_occupied_territory(self):
        """
        A move to a territory which is occupied where there is no support and
        no attacking pieces fails.
        """
        move = self.move(self.army, self.paris, self.gascony)
        self.set_piece_territory(self.german_army, self.gascony)
        models.Command.objects.create(
            piece=self.german_army,
            source=self.gascony,
            order=self.german_order,
            type=CommandType.HOLD,
        )
        self.assertTrue(move.unresolved)
        move.resolve()
        self.assertTrue(move.fails)

    def test_move_to_occupied_territory_but_piece_move_successfully(self):
        """
        A move to a territory which is occupied by a piece which successfully
        moves succeeds.
        """
        move = self.move(self.army, self.paris, self.gascony)
        self.set_piece_territory(self.german_army, self.gascony)
        models.Command.objects.create(
            piece=self.german_army,
            source=self.gascony,
            target=self.spain,
            order=self.german_order,
            type=CommandType.MOVE,
            state=CommandState.SUCCEEDS,
        )
        self.assertTrue(move.unresolved)
        move.resolve()
        self.assertTrue(move.succeeds)

    def test_move_with_support_to_occupied_territory_without_support(self):
        """
        A move with support to a territory which is occupied without support
        and no attacking pieces succeeds.
        """
        pass


class TestHeadToHead(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.france = models.Nation.objects.get(name='France')
        self.germany = models.Nation.objects.get(name='Germany')
        self.french_order = models.Order.objects.create(
            nation=self.france,
            turn=self.turn,
        )
        self.german_order = models.Order.objects.create(
            nation=self.germany,
            turn=self.turn,
        )
        self.french_army = models.Piece.objects.get(territory__name='paris')
        self.second_french_army = models.Piece.objects.get(territory__name='marseilles')
        self.german_army = models.Piece.objects.get(territory__name='munich')
        self.german_fleet = models.Piece.objects.get(territory__name='kiel')

    def test_head_to_head_battle_exists(self):
        """
        Two pieces from different nations attempting to move into eachother's
        territories causes a head-to-head battle.
        """
        self.set_piece_territory(self.german_army, self.burgundy)
        command = models.Command.objects.create(
            piece=self.french_army,
            source=self.paris,
            target=self.burgundy,
            order=self.french_order,
            type=CommandType.MOVE,
        )
        models.Command.objects.create(
            piece=self.german_army,
            source=self.burgundy,
            target=self.paris,
            order=self.german_order,
            type=CommandType.MOVE,
        )
        self.assertTrue(command.head_to_head_exists())

    def test_head_to_head_battle_same_nation(self):
        """
        Two pieces from the same nation attempting to move into eachother's
        territories does not cause a head-to-head battle.
        """
        self.set_piece_territory(self.second_french_army, self.burgundy)
        command = models.Command.objects.create(
            piece=self.french_army,
            source=self.paris,
            target=self.burgundy,
            order=self.french_order,
            type=CommandType.MOVE,
        )
        models.Command.objects.create(
            piece=self.german_army,
            source=self.burgundy,
            target=self.paris,
            order=self.french_order,
            type=CommandType.MOVE,
        )
        self.assertFalse(command.head_to_head_exists())

    def test_head_to_head_battle_moving_to_different_territory(self):
        """
        If a the piece in the target territory is moving to a territory other
        than the source of the given command, no head-to-head battle.
        """
        self.set_piece_territory(self.german_army, self.burgundy)
        command = models.Command.objects.create(
            piece=self.french_army,
            source=self.paris,
            target=self.burgundy,
            order=self.french_order,
            type=CommandType.MOVE,
        )
        models.Command.objects.create(
            piece=self.german_army,
            source=self.burgundy,
            target=self.picardy,
            order=self.german_order,
            type=CommandType.MOVE,
        )
        self.assertFalse(command.head_to_head_exists())

    def test_head_to_head_battle_hold(self):
        """
        If a the piece in the target territory is holds there is no
        head-to-head battle.
        """
        self.set_piece_territory(self.german_army, self.burgundy)
        command = models.Command.objects.create(
            piece=self.french_army,
            source=self.paris,
            target=self.burgundy,
            order=self.french_order,
            type=CommandType.MOVE,
        )
        models.Command.objects.create(
            piece=self.german_army,
            source=self.burgundy,
            order=self.german_order,
            type=CommandType.HOLD,
        )
        self.assertFalse(command.head_to_head_exists())

    def test_head_to_head_battle_piece_moving_into_target_territory(self):
        """
        If the enemy other piece is moving into the target territory, no
        head-to-head battle.
        """
        command = models.Command.objects.create(
            piece=self.french_army,
            source=self.paris,
            target=self.burgundy,
            order=self.french_order,
            type=CommandType.MOVE,
        )
        models.Command.objects.create(
            piece=self.german_army,
            source=self.munich,
            target=self.burgundy,
            order=self.german_order,
            type=CommandType.HOLD,
        )
        self.assertFalse(command.head_to_head_exists())
