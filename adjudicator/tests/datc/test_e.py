import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestHeadToHeadBattles(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_disloged_unit_has_not_effect_on_attackers_area(self):
        """
        An army can follow.

        Germany:
        A Berlin - Prussia
        F Kiel - Berlin
        A Silesia Supports A Berlin - Prussia

        Russia:
        A Prussia - Berlin

        The fleet in Kiel will move to Berlin.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Army(0, Nations.GERMANY, self.territories.SILESIA),
            Army(0, Nations.RUSSIA, self.territories.PRUSSIA),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.BERLIN, self.territories.PRUSSIA),
            Move(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN),
            Support(0, Nations.GERMANY, self.territories.SILESIA, self.territories.BERLIN, self.territories.PRUSSIA),
            Move(0, Nations.RUSSIA, self.territories.PRUSSIA, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertTrue(orders[0].move_decision, Outcomes.MOVES)
        self.assertTrue(orders[1].move_decision, Outcomes.MOVES)
        self.assertTrue(orders[2].support_decision, Outcomes.GIVEN)

    def test_no_self_dislodgement_in_head_to_head_battle(self):
        """
        Self dislodgement is not allowed. This also counts for head to head
        battles.

        Germany:
        A Berlin - Kiel
        F Kiel - Berlin
        A Munich Supports A Berlin - Kiel

        No unit will move.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Army(0, Nations.GERMANY, self.territories.MUNICH),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.BERLIN, self.territories.KIEL),
            Move(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN),
            Support(0, Nations.GERMANY, self.territories.MUNICH, self.territories.BERLIN, self.territories.KIEL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertTrue(orders[0].move_decision, Outcomes.FAILS)
        self.assertTrue(orders[1].move_decision, Outcomes.FAILS)
        self.assertTrue(orders[2].support_decision, Outcomes.GIVEN)

    def test_no_help_in_dislodging_own_unit(self):
        """
        To help a foreign power to dislodge own unit in head to head battle is
        not possible.

        Germany:
        A Berlin - Kiel
        A Munich Supports F Kiel - Berlin

        England:
        F Kiel - Berlin

        No unit will move.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Army(0, Nations.GERMANY, self.territories.MUNICH),
            Fleet(0, Nations.ENGLAND, self.territories.KIEL),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.BERLIN, self.territories.KIEL),
            Support(0, Nations.GERMANY, self.territories.MUNICH, self.territories.KIEL, self.territories.BERLIN),
            Move(0, Nations.ENGLAND, self.territories.KIEL, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertTrue(orders[0].move_decision, Outcomes.FAILS)
        self.assertTrue(orders[1].support_decision, Outcomes.GIVEN)
        self.assertTrue(orders[2].move_decision, Outcomes.FAILS)

    def test_non_dislodged_loser_has_still_effect(self):
        """
        If in an unbalanced head to head battle the loser is not dislodged, it
        has still effect on the area of the attacker.

        Germany:
        F Holland - North Sea
        F Helgoland Bight Supports F Holland - North Sea
        F Skagerrak Supports F Holland - North Sea

        France:
        F North Sea - Holland
        F Belgium Supports F North Sea - Holland

        England:
        F Edinburgh Supports F Norwegian Sea - North Sea
        F Yorkshire Supports F Norwegian Sea - North Sea
        F Norwegian Sea - North Sea

        Austria:
        A Kiel Supports A Ruhr - Holland
        A Ruhr - Holland

        The French fleet in the North Sea is not dislodged due to the
        beleaguered garrison. Therefore, the Austrian army in Ruhr will not
        move to Holland.
        """
        pieces = [
            Fleet(0, Nations.GERMANY, self.territories.HOLLAND),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.GERMANY, self.territories.SKAGERRAK),
            Fleet(0, Nations.FRANCE, self.territories.NORTH_SEA),
            Fleet(0, Nations.FRANCE, self.territories.BELGIUM),
            Fleet(0, Nations.ENGLAND, self.territories.EDINBURGH),
            Fleet(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.ENGLAND, self.territories.NORWEGIAN_SEA),
            Army(0, Nations.AUSTRIA, self.territories.KIEL),
            Army(0, Nations.AUSTRIA, self.territories.RUHR),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.HOLLAND, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.HOLLAND, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.SKAGERRAK, self.territories.HOLLAND, self.territories.NORTH_SEA),
            Move(0, Nations.FRANCE, self.territories.NORTH_SEA, self.territories.HOLLAND),
            Support(0, Nations.FRANCE, self.territories.BELGIUM, self.territories.NORTH_SEA, self.territories.HOLLAND),
            Support(0, Nations.ENGLAND, self.territories.EDINBURGH, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Support(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Move(0, Nations.ENGLAND, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Support(0, Nations.AUSTRIA, self.territories.KIEL, self.territories.RUHR, self.territories.HOLLAND),
            Move(0, Nations.AUSTRIA, self.territories.RUHR, self.territories.HOLLAND),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[6].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[7].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[8].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[9].move_decision, Outcomes.FAILS)

    def test_loser_dislodged_by_another_army_still_has_effect(self):
        """
        If in an unbalanced head to head battle the loser is dislodged by a
        unit not part of the head to head battle, the loser has still effect on
        the place of the winner of the head to head battle.
        Germany:
        F Holland - North Sea
        F Helgoland Bight Supports F Holland - North Sea
        F Skagerrak Supports F Holland - North Sea

        France:
        F North Sea - Holland
        F Belgium Supports F North Sea - Holland

        England:
        F Edinburgh Supports F Norwegian Sea - North Sea
        F Yorkshire Supports F Norwegian Sea - North Sea
        F Norwegian Sea - North Sea
        F London Supports F Norwegian Sea - North Sea

        Austria:
        A Kiel Supports A Ruhr - Holland
        A Ruhr - Holland

        The French fleet in the North Sea is dislodged but not by the German
        fleet in Holland. Therefore, the French fleet can still prevent that
        the Austrian army in Ruhr will move to Holland. So, the Austrian move
        in Ruhr fails and the German fleet in Holland is not dislodged.
        """
        pieces = [
            Fleet(0, Nations.GERMANY, self.territories.HOLLAND),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.GERMANY, self.territories.SKAGERRAK),
            Fleet(0, Nations.FRANCE, self.territories.NORTH_SEA),
            Fleet(0, Nations.FRANCE, self.territories.BELGIUM),
            Fleet(0, Nations.ENGLAND, self.territories.EDINBURGH),
            Fleet(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.ENGLAND, self.territories.NORWEGIAN_SEA),
            Fleet(0, Nations.ENGLAND, self.territories.LONDON),
            Army(0, Nations.AUSTRIA, self.territories.KIEL),
            Army(0, Nations.AUSTRIA, self.territories.RUHR),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.HOLLAND, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.HOLLAND, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.SKAGERRAK, self.territories.HOLLAND, self.territories.NORTH_SEA),
            Move(0, Nations.FRANCE, self.territories.NORTH_SEA, self.territories.HOLLAND),
            Support(0, Nations.FRANCE, self.territories.BELGIUM, self.territories.NORTH_SEA, self.territories.HOLLAND),
            Support(0, Nations.ENGLAND, self.territories.EDINBURGH, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Support(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Move(0, Nations.ENGLAND, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Support(0, Nations.ENGLAND, self.territories.LONDON, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Support(0, Nations.AUSTRIA, self.territories.KIEL, self.territories.RUHR, self.territories.HOLLAND),
            Move(0, Nations.AUSTRIA, self.territories.RUHR, self.territories.HOLLAND),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[7])
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[6].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[7].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[8].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[9].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[10].move_decision, Outcomes.FAILS)

    def test_no_self_dislodgement_with_beleauguered_garrison(self):
        """
        An attempt to self dislodge can be combined with a beleaguered
        garrison. Such self dislodgement is still not possible.

        England:
        F North Sea Hold
        F Yorkshire Supports F Norway - North Sea

        Germany:
        F Holland Supports F Helgoland Bight - North Sea
        F Helgoland Bight - North Sea

        Russia:
        F Skagerrak Supports F Norway - North Sea
        F Norway - North Sea

        Although the Russians beat the German attack (with the support of
        Yorkshire) and the two Russian fleets are enough to dislodge the fleet
        in the North Sea, the fleet in the North Sea is not dislodged, since it
        would not be dislodged if the English fleet in Yorkshire would not give
        support. According to the DPTG the fleet in the North Sea would be
        dislodged. The DPTG is incorrect in this case.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Fleet(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.GERMANY, self.territories.HOLLAND),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.RUSSIA, self.territories.SKAGERRAK),
            Fleet(0, Nations.RUSSIA, self.territories.NORWAY),
        ]
        orders = [
            Hold(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Support(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.NORWAY, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.HOLLAND, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Support(0, Nations.RUSSIA, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.NORTH_SEA),
            Move(0, Nations.RUSSIA, self.territories.NORWAY, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].move_decision, Outcomes.FAILS)

    def test_no_self_dislodgement_with_beleauguered_and_head_to_head(self):
        """
        Similar to the previous test case, but now the beleaguered fleet is
        also engaged in a head to head battle.

        England:
        F North Sea - Norway
        F Yorkshire Supports F Norway - North Sea

        Germany:
        F Holland Supports F Helgoland Bight - North Sea
        F Helgoland Bight - North Sea

        Russia:
        F Skagerrak Supports F Norway - North Sea
        F Norway - North Sea

        Again, none of the fleets move.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Fleet(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.GERMANY, self.territories.HOLLAND),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.RUSSIA, self.territories.SKAGERRAK),
            Fleet(0, Nations.RUSSIA, self.territories.NORWAY),
        ]
        orders = [
            Move(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.NORWAY),
            Support(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.NORWAY, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.HOLLAND, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Support(0, Nations.RUSSIA, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.NORTH_SEA),
            Move(0, Nations.RUSSIA, self.territories.NORWAY, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].move_decision, Outcomes.FAILS)

    def test_almost_self_dislodgement_with_beleaguered_garrison(self):
        """
        Similar to the previous test case, but now the beleaguered fleet is moving away.

        England:
        F North Sea - Norwegian Sea
        F Yorkshire Supports F Norway - North Sea

        Germany:
        F Holland Supports F Helgoland Bight - North Sea
        F Helgoland Bight - North Sea

        Russia:
        F Skagerrak Supports F Norway - North Sea
        F Norway - North Sea

        Both the fleet in the North Sea and the fleet in Norway move.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Fleet(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.GERMANY, self.territories.HOLLAND),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.RUSSIA, self.territories.SKAGERRAK),
            Fleet(0, Nations.RUSSIA, self.territories.NORWAY),
        ]
        orders = [
            Move(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.NORWEGIAN_SEA),
            Support(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.NORWAY, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.HOLLAND, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Support(0, Nations.RUSSIA, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.NORTH_SEA),
            Move(0, Nations.RUSSIA, self.territories.NORWAY, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].move_decision, Outcomes.MOVES)

    def test_almost_circular_movement_self_dislodgement_with_beleaguered_garrison(self):
        """
        Similar to the previous test case, but now the beleaguered fleet is in
        circular movement with the weaker attacker. So, the circular movement
        fails.

        England:
        F North Sea - Denmark
        F Yorkshire Supports F Norway - North Sea

        Germany:
        F Holland Supports F Helgoland Bight - North Sea
        F Helgoland Bight - North Sea
        F Denmark - Helgoland Bight

        Russia:
        F Skagerrak Supports F Norway - North Sea
        F Norway - North Sea

        There is no movement of fleets.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Fleet(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.GERMANY, self.territories.HOLLAND),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.GERMANY, self.territories.DENMARK),
            Fleet(0, Nations.RUSSIA, self.territories.SKAGERRAK),
            Fleet(0, Nations.RUSSIA, self.territories.NORWAY),
        ]
        orders = [
            Move(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.DENMARK),
            Support(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.NORWAY, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.HOLLAND, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.DENMARK, self.territories.HELGOLAND_BIGHT),
            Support(0, Nations.RUSSIA, self.territories.SKAGERRAK, self.territories.NORWAY, self.territories.NORTH_SEA),
            Move(0, Nations.RUSSIA, self.territories.NORWAY, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[5].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[6].move_decision, Outcomes.FAILS)

    def test_almost_circular_movement_self_dislodgement_coasts(self):
        """
        Similar to the previous test case, but now the beleaguered fleet is in
        a unit swap with the stronger attacker. So, the unit swap succeeds. To
        make the situation more complex, the swap is on an area with two
        coasts.

        France:
        A Spain - Portugal via Convoy
        F Mid-Atlantic Ocean Convoys A Spain - Portugal
        F Gulf of Lyon Supports F Portugal - Spain(nc)

        Germany:
        A Marseilles Supports A Gascony - Spain
        A Gascony - Spain

        Italy:
        F Portugal - Spain(nc)
        F Western Mediterranean Supports F Portugal - Spain(nc)

        The unit swap succeeds. Note that due to the success of the swap, there
        is no beleaguered garrison anymore.
        """

        pieces = [
            Army(0, Nations.FRANCE, self.territories.SPAIN),
            Fleet(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
            Fleet(0, Nations.FRANCE, self.territories.GULF_OF_LYON),
            Army(0, Nations.GERMANY, self.territories.MARSEILLES),
            Army(0, Nations.GERMANY, self.territories.GASCONY),
            Fleet(0, Nations.ITALY, self.territories.PORTUGAL),
            Fleet(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN),
        ]
        orders = [
            Move(0, Nations.FRANCE, self.territories.SPAIN, self.territories.PORTUGAL, via_convoy=True),
            Convoy(0, Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.SPAIN, self.territories.PORTUGAL),
            Support(0, Nations.FRANCE, self.territories.GULF_OF_LYON, self.territories.SPAIN, self.territories.PORTUGAL),
            Support(0, Nations.GERMANY, self.territories.MARSEILLES, self.territories.GASCONY, self.territories.SPAIN),
            Move(0, Nations.GERMANY, self.territories.GASCONY, self.territories.SPAIN),
            Move(0, Nations.ITALY, self.territories.PORTUGAL, self.territories.SPAIN, self.named_coasts.SPAIN_NC),
            Support(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN, self.territories.PORTUGAL, self.territories.SPAIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[5].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[6].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)

    def test_support_on_attack_on_own_unit_can_be_used_for_other_means(self):
        """
        A support on an attack on your own unit has still effect. It can
        prevent that another army will dislodge the unit.

        Austria:
        A Budapest - Rumania
        A Serbia Supports A Vienna - Budapest

        Italy:
        A Vienna - Budapest

        Russia:
        A Galicia - Budapest
        A Rumania Supports A Galicia - Budapest

        The support of Serbia on the Italian army prevents that the Russian
        army in Galicia will advance. No army will move.
        """
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.BUDAPEST),
            Army(0, Nations.AUSTRIA, self.territories.SERBIA),
            Army(0, Nations.ITALY, self.territories.VIENNA),
            Army(0, Nations.RUSSIA, self.territories.GALICIA),
            Army(0, Nations.RUSSIA, self.territories.RUMANIA),
        ]
        orders = [
            Move(0, Nations.AUSTRIA, self.territories.BUDAPEST, self.territories.RUMANIA),
            Support(0, Nations.AUSTRIA, self.territories.SERBIA, self.territories.VIENNA, self.territories.BUDAPEST),
            Move(0, Nations.ITALY, self.territories.VIENNA, self.territories.BUDAPEST),
            Move(0, Nations.RUSSIA, self.territories.GALICIA, self.territories.BUDAPEST),
            Support(0, Nations.RUSSIA, self.territories.RUMANIA, self.territories.GALICIA, self.territories.BUDAPEST),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)

    def test_three_way_beleaguered_garrison(self):
        """
        In a beleaguered garrison from three sides, the adjudicator may not let
        two attacks fail and then let the third succeed.

        England:
        F Edinburgh Supports F Yorkshire - North Sea
        F Yorkshire - North Sea

        France:
        F Belgium - North Sea
        F English Channel Supports F Belgium - North Sea

        Germany:
        F North Sea Hold

        Russia:
        F Norwegian Sea - North Sea
        F Norway Supports F Norwegian Sea - North Sea

        None of the fleets move. The German fleet in the North Sea is not
        dislodged.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.EDINBURGH),
            Fleet(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.FRANCE, self.territories.BELGIUM),
            Fleet(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
            Fleet(0, Nations.GERMANY, self.territories.NORTH_SEA),
            Fleet(0, Nations.RUSSIA, self.territories.NORWEGIAN_SEA),
            Fleet(0, Nations.RUSSIA, self.territories.NORWAY),
        ]
        orders = [
            Support(0, Nations.ENGLAND, self.territories.EDINBURGH, self.territories.YORKSHIRE, self.territories.NORTH_SEA),
            Move(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.NORTH_SEA),
            Move(0, Nations.FRANCE, self.territories.BELGIUM, self.territories.NORTH_SEA),
            Support(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.BELGIUM, self.territories.NORTH_SEA),
            Hold(0, Nations.GERMANY, self.territories.NORTH_SEA),
            Move(0, Nations.RUSSIA, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
            Support(0, Nations.RUSSIA, self.territories.NORWAY, self.territories.NORWEGIAN_SEA, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[4].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[6].support_decision, Outcomes.GIVEN)

    def test_illegal_head_to_head_battle_can_still_defend(self):
        """
        If in a head to head battle, one of the units makes an illegal move,
        than that unit has still the possibility to defend against attacks with
        strength of one.

        England:
        A Liverpool - Edinburgh

        Russia:
        F Edinburgh - Liverpool

        The move of the Russian fleet is illegal, but can still prevent the
        English army to enter Edinburgh. So, none of the units move.
        """
        pieces = [
            Army(0, Nations.ENGLAND, self.territories.LIVERPOOL),
            Fleet(0, Nations.RUSSIA, self.territories.EDINBURGH),
        ]
        orders = [
            Move(0, Nations.ENGLAND, self.territories.LIVERPOOL, self.territories.EDINBURGH),
            Move(0, Nations.RUSSIA, self.territories.EDINBURGH, self.territories.LIVERPOOL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)

    @unittest.skip('test_friendly_head_to_head_battle - recursion problem')
    def test_friendly_head_to_head_battle(self):
        """
        In this case both units in the head to head battle prevent that the
        other one is dislodged.

        England:
        F Holland Supports A Ruhr - Kiel
        A Ruhr - Kiel

        France:
        A Kiel - Berlin
        A Munich Supports A Kiel - Berlin
        A Silesia Supports A Kiel - Berlin

        Germany:
        A Berlin - Kiel
        F Denmark Supports A Berlin - Kiel
        F Helgoland Bight Supports A Berlin - Kiel

        Russia:
        F Baltic Sea Supports A Prussia - Berlin
        A Prussia - Berlin

        None of the moves succeeds. This case is especially difficult for
        sequence based adjudicators. They will start adjudicating the head to
        head battle and continue to adjudicate the attack on one of the units
        part of the head to head battle. In this process, one of the sides of
        the head to head battle might be cancelled out. This happens in the
        DPTG. If this is adjudicated according to the DPTG, the unit in Ruhr or
        in Prussia will advance (depending on the order the units are
        adjudicated). This is clearly a bug in the DPTG.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.HOLLAND),
            Army(0, Nations.ENGLAND, self.territories.RUHR),
            Army(0, Nations.FRANCE, self.territories.KIEL),
            Army(0, Nations.FRANCE, self.territories.MUNICH),
            Army(0, Nations.FRANCE, self.territories.SILESIA),
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.DENMARK),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.RUSSIA, self.territories.BALTIC_SEA),
            Army(0, Nations.RUSSIA, self.territories.PRUSSIA),
        ]
        orders = [
            Support(0, Nations.ENGLAND, self.territories.HOLLAND, self.territories.RUHR, self.territories.KIEL),
            Move(0, Nations.ENGLAND, self.territories.RUHR, self.territories.KIEL),
            Move(0, Nations.FRANCE, self.territories.KIEL, self.territories.BERLIN),
            Support(0, Nations.FRANCE, self.territories.MUNICH, self.territories.KIEL, self.territories.BERLIN),
            Support(0, Nations.FRANCE, self.territories.SILESIA, self.territories.KIEL, self.territories.BERLIN),
            Move(0, Nations.GERMANY, self.territories.BERLIN, self.territories.KIEL),
            Support(0, Nations.GERMANY, self.territories.DENMARK, self.territories.BERLIN, self.territories.KIEL),
            Support(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.BERLIN, self.territories.KIEL),
            Support(0, Nations.RUSSIA, self.territories.BALTIC_SEA, self.territories.PRUSSIA, self.territories.BERLIN),
            Move(0, Nations.RUSSIA, self.territories.PRUSSIA, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[5].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[9].move_decision, Outcomes.FAILS)
