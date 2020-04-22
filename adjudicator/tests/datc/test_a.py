import unittest

from adjudicator import illegal_messages
from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import Nations, Territories, register_all


class TestBasicChecks(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.state = register_all(self.state, self.territories, [])

    def test_moving_to_an_area_that_is_not_a_neighbour(self):
        """
        Check if an illegal move (without convoy) will fail.

        England:
        F North Sea - Picardy

        Order should fail.
        """
        fleet = Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA)
        order = Move(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.PICARDY)

        self.state.register(fleet, order)
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.M004)

    def test_move_army_to_sea(self):
        """
        Check if an army could not be moved to open sea.

        England:
        A Liverpool - Irish Sea

        Order should fail.
        """
        army = Army(0, Nations.ENGLAND, self.territories.LIVERPOOL)
        order = Move(0, Nations.ENGLAND, self.territories.LIVERPOOL, self.territories.IRISH_SEA)

        self.state.register(army, order)
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.M005)

    def test_move_fleet_to_land(self):
        """
        Check whether a fleet can not move to land.

        Germany:
        F Kiel - Munich

        Order should fail.
        """
        fleet = Fleet(0, Nations.GERMANY, self.territories.KIEL)
        order = Move(0, Nations.GERMANY, self.territories.KIEL, self.territories.MUNICH)

        self.state.register(fleet, order)
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.M006)

    def test_move_to_own_sector(self):
        """
        Moving to the same sector is an illegal move (2000 rulebook, page 4,
        "An Army can be ordered to move into an adjacent inland or coastal
        province.").

        Germany:
        F Kiel - Kiel

        Program should not crash.
        """
        army = Army(0, Nations.GERMANY, self.territories.KIEL)
        order = Move(0, Nations.GERMANY, self.territories.KIEL, self.territories.KIEL)

        self.state.register(army, order)
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.M002)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Army(0, Nations.ENGLAND, self.territories.LIVERPOOL),
            Fleet(0, Nations.ENGLAND, self.territories.LONDON),
            Army(0, Nations.ENGLAND, self.territories.WALES),
        ]

        fleet_north_sea_convoy = Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.YORKSHIRE, self.territories.YORKSHIRE)
        army_yorkshire_move = Move(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.YORKSHIRE)
        army_liverpool_support = Support(0, Nations.ENGLAND, self.territories.LIVERPOOL, self.territories.YORKSHIRE, self.territories.YORKSHIRE)
        fleet_london_move = Move(0, Nations.GERMANY, self.territories.LONDON, self.territories.YORKSHIRE)
        army_wales_support = Support(0, Nations.GERMANY, self.territories.WALES, self.territories.LONDON, self.territories.YORKSHIRE)

        self.state.register(
            *pieces, fleet_north_sea_convoy, army_yorkshire_move, army_liverpool_support,
            fleet_london_move, army_wales_support)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(army_yorkshire_move.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(army_yorkshire_move.illegal_message, illegal_messages.M002)

    def test_ordering_a_unit_of_another_country(self):
        """
        Check whether someone can not order a unit that does not belong to them.

        England has a fleet in London.

        Germany:
        F London - North Sea

        Order should fail.
        """
        fleet = Fleet(0, Nations.ENGLAND, self.territories.LONDON)
        order = Move(0, Nations.GERMANY, self.territories.LONDON, self.territories.NORTH_SEA)

        self.state.register(fleet, order)
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.A001)

    def test_only_armies_can_be_convoyed(self):
        """
        A fleet can not be convoyed.

        England:
        F London - Belgium
        F North Sea Convoys A London - Belgium

        Move from London to Belgium should fail.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
        ]
        fleet_london_move = Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True)
        fleet_north_sea_convoy = Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM)

        self.state.register(*pieces, fleet_london_move, fleet_north_sea_convoy)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(fleet_london_move.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(fleet_london_move.illegal_message, illegal_messages.M004)

        self.assertEqual(fleet_north_sea_convoy.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(fleet_north_sea_convoy.illegal_message, illegal_messages.C001)

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
        pieces = [
            Army(0, Nations.ITALY, self.territories.VENICE),
            Army(0, Nations.ITALY, self.territories.TYROLIA),
            Fleet(0, Nations.AUSTRIA, self.territories.TRIESTE)
        ]

        # TODO finish
        army_venice_move = Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TRIESTE)
        army_tyrolia_support = Support(0, Nations.ITALY, self.territories.TYROLIA, self.territories.VENICE, self.territories.TRIESTE)
        fleet_trieste_support = Support(0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.TRIESTE, self.territories.TRIESTE)

        self.state.register(*pieces, army_venice_move, army_tyrolia_support, fleet_trieste_support)
        process(self.state)

        self.assertEqual(fleet_trieste_support.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(fleet_trieste_support.illegal_message, illegal_messages.S001)

    def test_fleet_must_follow_coast_if_not_on_sea(self):
        """
        If two places are adjacent, that does not mean that a fleet can move
        between those two places. An implementation that only holds one list of
        adjacent places for each place, is incorrect.

        Italy:
        F Rome - Venice

        Move fails. An army can go from Rome to Venice, but a fleet can not.
        """
        fleet = Fleet(0, Nations.ITALY, self.territories.ROME, self.territories.VENICE)
        order = Move(0, Nations.ITALY, self.territories.ROME, self.territories.VENICE)

        self.state.register(order, fleet)
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.M007)

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
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.VENICE),
            Fleet(0, Nations.ITALY, self.territories.ROME),
            Army(0, Nations.ITALY, self.territories.APULIA)
        ]

        # TODO finish
        army_austria_hold = Hold(0, Nations.AUSTRIA, self.territories.VENICE)
        fleet_rome_support = Support(0, Nations.ITALY, self.territories.ROME, self.territories.APULIA, self.territories.VENICE)
        army_apulia_move = Move(0, Nations.ITALY, self.territories.APULIA, self.territories.VENICE)

        self.state.register(*pieces, army_austria_hold, fleet_rome_support, army_apulia_move)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(fleet_rome_support.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(fleet_rome_support.illegal_message, illegal_messages.S002)

    def test_simple_bounce(self):
        """
        Two armies bouncing on each other.

        Austria:
        A Vienna - Tyrolia

        Italy:
        A Venice - Tyrolia

        The two units bounce.
        """
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.VIENNA),
            Army(0, Nations.ITALY, self.territories.VENICE),
        ]

        army_vienna_move = Move(0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.TYROLIA)
        army_venice_move = Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TYROLIA)

        self.state.register(*pieces, army_venice_move, army_vienna_move)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(army_venice_move.legal_decision, Outcomes.LEGAL)
        self.assertEqual(army_vienna_move.legal_decision, Outcomes.LEGAL)

        self.assertEqual(army_vienna_move.move_decision, Outcomes.FAILS)
        self.assertEqual(army_venice_move.move_decision, Outcomes.FAILS)

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
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.VIENNA),
            Army(0, Nations.ITALY, self.territories.VENICE),
            Army(0, Nations.GERMANY, self.territories.MUNICH)
        ]

        army_vienna_move = Move(0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.TYROLIA)
        army_venice_move = Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TYROLIA)
        army_munich_move = Move(0, Nations.GERMANY, self.territories.MUNICH, self.territories.TYROLIA)

        self.state.register(*pieces, army_venice_move, army_vienna_move, army_munich_move)
        process(self.state)

        self.assertEqual(army_venice_move.legal_decision, Outcomes.LEGAL)
        self.assertEqual(army_vienna_move.legal_decision, Outcomes.LEGAL)
        self.assertEqual(army_munich_move.legal_decision, Outcomes.LEGAL)

        self.assertEqual(army_vienna_move.move_decision, Outcomes.FAILS)
        self.assertEqual(army_venice_move.move_decision, Outcomes.FAILS)
        self.assertEqual(army_munich_move.move_decision, Outcomes.FAILS)
