import unittest

from core import models
from core.models.base import DislodgedState
from core.utils.command import convoy, hold, move, support
from core.utils.piece import army, fleet
from core.tests.base import HelperMixin, TerritoriesMixin
from core.tests.base import InitialGameStateTestCase as TestCase


class TestBasicChecks(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.initialise_nations()
        self.initialise_orders()

    def test_moving_to_an_area_that_is_not_a_neighbour(self):
        """
        Check if an illegal move (without convoy) will fail.

        England:
        F North Sea - Picardy

        Order should fail.
        """
        fleet_north_sea = fleet(self.turn, self.england, self.north_sea)
        c = move(self.england_order, fleet_north_sea, self.north_sea,
                 self.picardy)

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(c.illegal)
        self.assertEqual(
            c.illegal_message,
            'Fleet North Sea cannot reach Picardy.'
        )

    def test_move_army_to_sea(self):
        """
        Check if an army could not be moved to open sea.

        England:
        A Liverpool - Irish Sea

        Order should fail.
        """
        army_liverpool = army(self.turn, self.england, self.liverpool)
        c = move(self.england_order, army_liverpool, self.liverpool,
                 self.irish_sea)

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(c.illegal)
        self.assertEqual(
            c.illegal_message,
            'Army Liverpool cannot reach Irish Sea.'
        )

    def test_move_fleet_to_land(self):
        """
        Check whether a fleet can not move to land.

        Germany:
        F Kiel - Munich

        Order should fail.
        """
        fleet_kiel = fleet(self.turn, self.germany, self.kiel)
        c = move(self.germany_order, fleet_kiel, self.kiel,
                 self.munich)

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(c.illegal)
        self.assertEqual(
            c.illegal_message,
            'Fleet Kiel cannot reach Munich.'
        )

    def test_move_to_own_sector(self):
        """
        Moving to the same sector is an illegal move (2000 rulebook, page 4,
        "An Army can be ordered to move into an adjacent inland or coastal
        province.").

        Germany:
        F Kiel - Kiel

        Program should not crash.
        """
        fleet_kiel = fleet(self.turn, self.germany, self.kiel)
        c = move(self.germany_order, fleet_kiel, self.kiel,
                 self.kiel)

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(c.illegal)
        self.assertEqual(
            c.illegal_message,
            'Fleet Kiel cannot move to its own territory.'
        )

    @unittest.skip
    def test_move_to_own_sector_with_convoy(self):
        """
        Moving to the same sector is still illegal with convoy (2000 rulebook,
        page 4, "Note: An Army can move across water provinces from one coastal
        province to another...").

        England:
        F North Sea Convoys A Yorkshire - Yorkshire
        A Yorkshire - Yorkshire
        A Liverpool Supports A Yorkshire - Yorkshire

        Germany:
        F London - Yorkshire
        A Wales Supports F London - Yorkshire

        The move of the army in Yorkshire is illegal. This makes the support of
        Liverpool also illegal and without the support, the Germans have a
        stronger force. The fleet in London dislodges the army in Yorkshire.
        """
        fleet_north_sea = fleet(self.turn, self.england, self.north_sea)
        army_yorkshire = army(self.turn, self.england, self.yorkshire)
        army_liverpool = army(self.turn, self.england, self.liverpool)

        fleet_london = fleet(self.turn, self.germany, self.london)
        army_wales = army(self.turn, self.germany, self.wales)

        fleet_north_sea_convoy = convoy(
            self.england_order, fleet_north_sea, self.north_sea,
            self.yorkshire, self.yorkshire
        )
        army_yorkshire_move = move(
            self.england_order, army_yorkshire, self.yorkshire,
            self.yorkshire,
        )
        army_liverpool_support = support(
            self.england_order, army_liverpool, self.liverpool,
            self.yorkshire, self.yorkshire
        )
        fleet_london_move = move(
            self.germany_order, fleet_london, self.london, self.yorkshire,
        )
        army_wales_support = support(
            self.germany_order, army_wales, self.wales, self.london,
            self.yorkshire
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]
        print('nothing happening here')

    def test_ordering_a_unit_of_another_country(self):
        """
        Check whether someone can not order a unit that is not his own unit.

        England has a fleet in London.

        Germany:
        F London - North Sea

        Order should fail.
        """
        fleet_london = fleet(self.turn, self.england, self.london)
        c = move(
            self.germany_order, fleet_london, self.london,
            self.north_sea,
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(c.illegal)
        self.assertEqual(
            c.illegal_message,
            'No friendly piece exists in London.'
        )

    def test_only_armies_can_be_convoyed(self):
        """
        A fleet can not be convoyed.

        England:
        F London - Belgium
        F North Sea Convoys A London - Belgium

        Move from London to Belgium should fail.
        """
        fleet_london = fleet(self.turn, self.england, self.london)
        fleet_north_sea = fleet(self.turn, self.england, self.north_sea)
        fleet_london_move = move(
            self.england_order, fleet_london, self.london,
            self.belgium,
        )
        fleet_north_sea_convoy = convoy(
            self.england_order, fleet_north_sea, self.north_sea,
            self.london, self.belgium
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_london_move.illegal)
        self.assertTrue(fleet_north_sea_convoy.illegal)
        self.assertEqual(
            fleet_london_move.illegal_message,
            'Fleet London cannot reach Belgium.'
        )

    def test_support_to_hold_yourself_not_possible(self):
        """
        An army can not get an additional hold power by supporting itself.

        Italy:
        A Venice - Trieste
        A Tyrolia Supports A Venice - Trieste

        Austria:
        F Trieste Supports F Trieste

        The fleet in Trieste should be dislodged.
        """
        army_venice = army(self.turn, self.italy, self.venice)
        army_tyrolia = army(self.turn, self.italy, self.tyrolia)
        fleet_trieste = fleet(self.turn, self.austria, self.trieste)

        army_venice_move = move(
            self.italy_order, army_venice, self.venice, self.trieste,
        )
        army_tyrolia_support = support(
            self.italy_order, army_tyrolia, self.tyrolia, self.venice,
            self.trieste
        )
        fleet_trieste_support = support(
            self.austria_order, fleet_trieste, self.trieste, self.trieste,
            self.trieste
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_trieste_support.illegal)
        self.assertEqual(
            fleet_trieste_support.illegal_message,
            'Fleet Trieste cannot support its own territory.'
        )
        self.assertEqual(
            fleet_trieste.dislodged_by,
            army_venice
        )
        self.assertTrue(army_tyrolia_support.succeeds)

    def test_fleet_must_follow_coast_if_not_on_sea(self):
        """
        If two places are adjacent, that does not mean that a fleet can move
        between those two places. An implementation that only holds one list of
        adjacent places for each place, is incorrect.

        Italy:
        F Rome - Venice

        Move fails. An army can go from Rome to Venice, but a fleet can not.
        """
        fleet_rome = fleet(self.turn, self.italy, self.rome)
        command = move(
            self.italy_order, fleet_rome, self.rome, self.venice,
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(command.illegal)
        self.assertEqual(
            command.illegal_message,
            'Fleet Rome cannot reach Venice.'
        )

    def test_support_on_unreachable_destination_not_possible(self):
        """
        The destination of the move that is supported must be reachable by the
        supporting unit.

        Austria:
        A Venice Hold

        Italy:
        F Rome Supports A Apulia - Venice
        A Apulia - Venice

        The support of Rome is illegal, because Venice can not be reached from
        Rome by a fleet. Venice is not dislodged.
        """
        army_venice = army(self.turn, self.austria, self.venice)
        fleet_rome = fleet(self.turn, self.italy, self.rome)
        army_apulia = army(self.turn, self.italy, self.apulia)

        army_venice_hold = hold(
            self.austria_order, army_venice, self.venice
        )
        fleet_rome_support = support(
            self.italy_order, fleet_rome, self.rome, self.apulia, self.venice
        )
        army_apulia_move = move(
            self.italy_order, army_apulia, self.apulia, self.venice
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_rome_support.illegal)
        self.assertEqual(
            fleet_rome_support.illegal_message,
            'Fleet Rome cannot reach Venice.'
        )
        self.assertTrue(army_venice.dislodged_state == DislodgedState.SUSTAINS)
        self.assertTrue(army_apulia_move.fails)

    def test_simple_bounce(self):
        """
        Two armies bouncing on each other.

        Austria:
        A Vienna - Tyrolia

        Italy:
        A Venice - Tyrolia

        The two units bounce.
        """
        army_vienna = army(self.turn, self.austria, self.vienna)
        army_venice = army(self.turn, self.italy, self.venice)

        army_vienna_move = move(
            self.austria_order, army_vienna, self.vienna, self.tyrolia
        )
        army_venice_move = move(
            self.italy_order, army_venice, self.venice, self.tyrolia
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(army_vienna_move.fails)
        self.assertFalse(army_vienna.dislodged)

        self.assertTrue(army_venice_move.fails)
        self.assertFalse(army_venice.dislodged)

    def test_bounce_of_three_units(self):
        """
        If three units move to the same place, the adjudicator should not
        bounce the first two units and then let the third unit go to the now
        open place.

        Austria:
        A Vienna - Tyrolia

        Germany:
        A Munich - Tyrolia

        Italy:
        A Venice - Tyrolia

        The three units bounce.
        """
        army_vienna = army(self.turn, self.austria, self.vienna)
        army_munich = army(self.turn, self.germany, self.munich)
        army_venice = army(self.turn, self.italy, self.venice)

        army_vienna_move = move(
            self.austria_order, army_vienna, self.vienna, self.tyrolia
        )
        army_venice_move = move(
            self.italy_order, army_venice, self.venice, self.tyrolia
        )
        army_munich_move = move(
            self.germany_order, army_munich, self.munich, self.tyrolia
        )

        models.Command.objects.process()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(army_vienna_move.fails)
        self.assertFalse(army_vienna.dislodged)

        self.assertTrue(army_venice_move.fails)
        self.assertFalse(army_venice.dislodged)

        self.assertTrue(army_munich_move.fails)
        self.assertFalse(army_munich.dislodged)
