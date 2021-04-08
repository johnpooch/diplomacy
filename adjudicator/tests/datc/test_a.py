import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.tests.data import Nations, Territories

from ..base import AdjudicatorTestCaseMixin


class TestBasicChecks(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.territories = Territories(self.state)

    def test_moving_to_an_area_that_is_not_a_neighbour(self):
        """
        Check if an illegal move (without convoy) will fail.

        England:
        F North Sea - Picardy

        Order should fail.
        """
        Fleet(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA)
        order = Move(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.PICARDY)

        process(self.state)

        self.assertTrue(order.illegal)
        self.assertEqual(order.outcome, Outcomes.FAILS)
        self.assertEqual(order.illegal_code, '004')
        self.assertEqual(
            order.illegal_verbose,
            'Fleet cannot reach non-adjacent territory.'
        )

    def test_move_army_to_sea(self):
        """
        Check if an army could not be moved to open sea.

        England:
        A Liverpool - Irish Sea

        Order should fail.
        """
        Army(self.state, 0, Nations.ENGLAND, self.territories.LIVERPOOL)
        order = Move(self.state, 0, Nations.ENGLAND, self.territories.LIVERPOOL, self.territories.IRISH_SEA)

        process(self.state)

        self.assertTrue(order.illegal)
        self.assertEqual(order.outcome, Outcomes.FAILS)
        self.assertEqual(order.illegal_code, '005')
        self.assertEqual(
            order.illegal_verbose,
            'Army cannot enter a sea territory'
        )

    def test_move_fleet_to_land(self):
        """
        Check whether a fleet can not move to land.

        Germany:
        F Kiel - Munich

        Order should fail.
        """
        Fleet(self.state, 0, Nations.GERMANY, self.territories.KIEL)
        order = Move(self.state, 0, Nations.GERMANY, self.territories.KIEL, self.territories.MUNICH)

        process(self.state)

        self.assertTrue(order.illegal)
        self.assertEqual(order.outcome, Outcomes.FAILS)
        self.assertEqual(
            order.illegal_code,
            '006'
        )
        self.assertEqual(
            order.illegal_verbose,
            'Fleet cannot enter an inland territory',
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
        Army(self.state, 0, Nations.GERMANY, self.territories.KIEL)
        order = Move(self.state, 0, Nations.GERMANY, self.territories.KIEL, self.territories.KIEL)

        process(self.state)

        self.assertTrue(order.illegal)
        self.assertEqual(order.illegal_code, '002')
        self.assertEqual(
            order.illegal_verbose,
            'Source and target cannot be the same territory.'
        )

    # TODO more checks here
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
        Fleet(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA),
        Army(self.state, 0, Nations.ENGLAND, self.territories.YORKSHIRE),
        Army(self.state, 0, Nations.ENGLAND, self.territories.LIVERPOOL),
        Fleet(self.state, 0, Nations.GERMANY, self.territories.LONDON),
        Army(self.state, 0, Nations.GERMANY, self.territories.WALES),

        Convoy(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.YORKSHIRE, self.territories.YORKSHIRE)
        army_yorkshire_move = Move(self.state, 0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.YORKSHIRE)
        Support(self.state, 0, Nations.ENGLAND, self.territories.LIVERPOOL, self.territories.YORKSHIRE, self.territories.YORKSHIRE)
        Move(self.state, 0, Nations.GERMANY, self.territories.LONDON, self.territories.YORKSHIRE)
        Support(self.state, 0, Nations.GERMANY, self.territories.WALES, self.territories.LONDON, self.territories.YORKSHIRE)

        process(self.state)

        self.assertTrue(army_yorkshire_move.illegal)
        self.assertEqual(army_yorkshire_move.outcome, Outcomes.FAILS)
        self.assertEqual(army_yorkshire_move.illegal_code, '002')
        self.assertEqual(
            army_yorkshire_move.illegal_verbose,
            'Source and target cannot be the same territory.'
        )

    def test_ordering_a_unit_of_another_country(self):
        """
        Check whether someone can not order a unit that does not belong to
        them.

        England has a fleet in London.

        Germany:
        F London - North Sea

        Order should fail.
        """
        Fleet(self.state, 0, Nations.ENGLAND, self.territories.LONDON)
        order = Move(self.state, 0, Nations.GERMANY, self.territories.LONDON, self.territories.NORTH_SEA)
        Hold(self.state, 0, Nations.ENGLAND, self.territories.LONDON)

        process(self.state)

        self.assertTrue(order.illegal)
        self.assertEqual(order.illegal_code, '001')
        self.assertEqual(
            order.illegal_verbose,
            'Cannot order a piece belonging to another nation.'
        )

    def test_only_armies_can_be_convoyed(self):
        """
        A fleet can not be convoyed.

        England:
        F London - Belgium
        F North Sea Convoys A London - Belgium

        Move from London to Belgium should fail.
        """
        Fleet(self.state, 0, Nations.ENGLAND, self.territories.LONDON),
        Fleet(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA),
        fleet_london_move = Move(self.state, 0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True)
        fleet_north_sea_convoy = Convoy(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM)

        process(self.state)

        self.assertTrue(fleet_london_move.illegal)
        self.assertTrue(fleet_london_move.outcome == Outcomes.FAILS)
        self.assertEqual(fleet_london_move.illegal_code, '004')
        self.assertEqual(
            fleet_london_move.illegal_verbose,
            'Fleet cannot reach non-adjacent territory.'
        )

        self.assertTrue(fleet_north_sea_convoy.illegal)
        self.assertEqual(
            fleet_north_sea_convoy.illegal_verbose,
            'Cannot convoy a fleet.'
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
        Army(self.state, 0, Nations.ITALY, self.territories.VENICE),
        Army(self.state, 0, Nations.ITALY, self.territories.TYROLIA),
        Fleet(self.state, 0, Nations.AUSTRIA, self.territories.TRIESTE)

        Move(self.state, 0, Nations.ITALY, self.territories.VENICE, self.territories.TRIESTE)
        Support(self.state, 0, Nations.ITALY, self.territories.TYROLIA, self.territories.VENICE, self.territories.TRIESTE)
        fleet_trieste_support = Support(self.state, 0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.TRIESTE, self.territories.TRIESTE)

        process(self.state)

        self.assertTrue(fleet_trieste_support.illegal)
        self.assertEqual(
            fleet_trieste_support.illegal_verbose,
            'Source and target cannot be the same territory.'
        )

    def test_fleet_must_follow_coast_if_not_on_sea(self):
        """
        If two places are adjacent, that does not mean that a fleet can move
        between those two places. An implementation that only holds one list of
        adjacent places for each place, is incorrect.

        Italy:
        F Rome - Venice

        Move fails. An army can go from Rome to Venice, but a fleet can not.
        """
        Fleet(self.state, 0, Nations.ITALY, self.territories.ROME)
        order = Move(self.state, 0, Nations.ITALY, self.territories.ROME, self.territories.VENICE)

        process(self.state)

        self.assertTrue(order.illegal)
        self.assertEqual(order.illegal_code, '007')
        self.assertEqual(
            order.illegal_verbose,
            'Fleet cannot reach coastal territory without shared coastline.'
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
        Army(self.state, 0, Nations.AUSTRIA, self.territories.VENICE),
        Fleet(self.state, 0, Nations.ITALY, self.territories.ROME),
        Army(self.state, 0, Nations.ITALY, self.territories.APULIA)

        # TODO finish
        Hold(self.state, 0, Nations.AUSTRIA, self.territories.VENICE)
        fleet_rome_support = Support(self.state, 0, Nations.ITALY, self.territories.ROME, self.territories.APULIA, self.territories.VENICE)
        Move(self.state, 0, Nations.ITALY, self.territories.APULIA, self.territories.VENICE)

        process(self.state)

        self.assertTrue(fleet_rome_support.illegal)
        self.assertEqual(fleet_rome_support.illegal_code, '010')
        self.assertEqual(
            fleet_rome_support.illegal_verbose,
            'Piece cannot reach that territory.'
        )

    def test_simple_bounce(self):
        """
        Two armies bouncing on each other.

        Austria:
        A Vienna - Tyrolia

        Italy:
        A Venice - Tyrolia

        The two units bounce.
        """
        Army(self.state, 0, Nations.AUSTRIA, self.territories.VIENNA),
        Army(self.state, 0, Nations.ITALY, self.territories.VENICE),

        army_vienna_move = Move(self.state, 0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.TYROLIA)
        army_venice_move = Move(self.state, 0, Nations.ITALY, self.territories.VENICE, self.territories.TYROLIA)

        process(self.state)

        self.assertTrue(army_venice_move.legal)
        self.assertTrue(army_vienna_move.legal)

        self.assertEqual(army_vienna_move.outcome, Outcomes.FAILS)
        self.assertEqual(army_venice_move.outcome, Outcomes.FAILS)

        # TODO
        # self.assertFalse(army_vienna.dislodged)
        # self.assertFalse(army_venice.dislodged)

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
        Army(self.state, 0, Nations.AUSTRIA, self.territories.VIENNA),
        Army(self.state, 0, Nations.ITALY, self.territories.VENICE),
        Army(self.state, 0, Nations.GERMANY, self.territories.MUNICH)

        army_vienna_move = Move(self.state, 0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.TYROLIA)
        army_venice_move = Move(self.state, 0, Nations.ITALY, self.territories.VENICE, self.territories.TYROLIA)
        army_munich_move = Move(self.state, 0, Nations.GERMANY, self.territories.MUNICH, self.territories.TYROLIA)

        process(self.state)

        self.assertTrue(army_venice_move.legal)
        self.assertTrue(army_vienna_move.legal)
        self.assertTrue(army_munich_move.legal)

        self.assertEqual(army_vienna_move.outcome, Outcomes.FAILS)
        self.assertEqual(army_venice_move.outcome, Outcomes.FAILS)
        self.assertEqual(army_munich_move.outcome, Outcomes.FAILS)
