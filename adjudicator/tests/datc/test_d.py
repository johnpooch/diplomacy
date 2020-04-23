import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestCircularMovement(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_support_hold_can_prevent_dislodgement(self):
        """
        The most simple support to hold order.

        Austria:
        F Adriatic Sea Supports A Trieste - Venice
        A Trieste - Venice

        Italy:
        A Venice Hold
        A Tyrolia Supports A Venice

        The support of Tyrolia prevents that the army in Venice is dislodged.
        The army in Trieste will not move.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.ADRIATIC_SEA),
            Army(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.ITALY, self.territories.VENICE),
            Army(0, Nations.ITALY, self.territories.TYROLIA)
        ]
        orders = [
            Support(0, Nations.AUSTRIA, self.territories.ADRIATIC_SEA, self.territories.TRIESTE, self.territories.VENICE),
            Move(0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.VENICE),
            Hold(0, Nations.ITALY, self.territories.VENICE),
            Support(0, Nations.ITALY, self.territories.TYROLIA, self.territories.VENICE, self.territories.VENICE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertTrue(orders[0].support_decision, Outcomes.GIVEN)
        self.assertTrue(orders[1].move_decision, Outcomes.FAILS)
        self.assertTrue(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.SUSTAINS)

    def test_move_cuts_support_on_hold(self):
        """
        The most simple support on hold cut.

        Austria:
        F Adriatic Sea Supports A Trieste - Venice
        A Trieste - Venice
        A Vienna - Tyrolia

        Italy:
        A Venice Hold
        A Tyrolia Supports A Venice

        The support of Tyrolia is cut by the army in Vienna. That means that
        the army in Venice is dislodged by the army from Trieste.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.ADRIATIC_SEA),
            Army(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.AUSTRIA, self.territories.VIENNA),
            Army(0, Nations.ITALY, self.territories.VENICE),
            Army(0, Nations.ITALY, self.territories.TYROLIA)
        ]
        orders = [
            Support(0, Nations.AUSTRIA, self.territories.ADRIATIC_SEA, self.territories.TRIESTE, self.territories.VENICE),
            Move(0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.VENICE),
            Move(0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.TYROLIA),
            Hold(0, Nations.ITALY, self.territories.VENICE),
            Support(0, Nations.ITALY, self.territories.TYROLIA, self.territories.VENICE, self.territories.VENICE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.CUT)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[1])

    def test_move_cuts_support_on_move(self):
        """
        The most simple support on move cut.

        Austria:
        F Adriatic Sea Supports A Trieste - Venice
        A Trieste - Venice

        Italy:
        A Venice Hold
        F Ionian Sea - Adriatic Sea

        The support of the fleet in the Adriatic Sea is cut. That means that
        the army in Venice will not be dislodged and the army in Trieste stays
        in Trieste.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.ADRIATIC_SEA),
            Army(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.ITALY, self.territories.VENICE),
            Fleet(0, Nations.AUSTRIA, self.territories.IONIAN_SEA),
        ]
        orders = [
            Support(0, Nations.AUSTRIA, self.territories.ADRIATIC_SEA, self.territories.TRIESTE, self.territories.VENICE),
            Move(0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.VENICE),
            Hold(0, Nations.ITALY, self.territories.VENICE),
            Move(0, Nations.ITALY, self.territories.IONIAN_SEA, self.territories.ADRIATIC_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.CUT)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.SUSTAINS)

    def test_support_to_hold_on_unit_supporting_a_hold_allowed(self):
        """
        A unit that is supporting a hold, can receive a hold support.

        Germany:
        A Berlin Supports F Kiel
        F Kiel Supports A Berlin

        Russia:
        F Baltic Sea Supports A Prussia - Berlin
        A Prussia - Berlin

        The Russian move from Prussia to Berlin fails.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Fleet(0, Nations.RUSSIA, self.territories.BALTIC_SEA),
            Army(0, Nations.RUSSIA, self.territories.PRUSSIA),
        ]
        orders = [
            Support(0, Nations.GERMANY, self.territories.BERLIN, self.territories.KIEL, self.territories.KIEL),
            Support(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN, self.territories.BERLIN),
            Support(0, Nations.RUSSIA, self.territories.BALTIC_SEA, self.territories.PRUSSIA, self.territories.BERLIN),
            Move(0, Nations.RUSSIA, self.territories.PRUSSIA, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.CUT)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)

    def test_support_to_hold_on_unit_supporting_a_move_allowed(self):
        """
        A unit that is supporting a move, can receive a hold support.

        Germany:
        A Berlin Supports A Munich - Silesia
        F Kiel Supports A Berlin
        A Munich - Silesia

        Russia:
        F Baltic Sea Supports A Prussia - Berlin
        A Prussia - Berlin

        The Russian move from Prussia to Berlin fails.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Army(0, Nations.GERMANY, self.territories.KIEL),
            Army(0, Nations.GERMANY, self.territories.MUNICH),
            Fleet(0, Nations.RUSSIA, self.territories.BALTIC_SEA),
            Army(0, Nations.RUSSIA, self.territories.PRUSSIA),
        ]
        orders = [
            Support(0, Nations.GERMANY, self.territories.BERLIN, self.territories.MUNICH, self.territories.SILESIA),
            Support(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN, self.territories.BERLIN),
            Move(0, Nations.GERMANY, self.territories.MUNICH, self.territories.SILESIA),
            Support(0, Nations.RUSSIA, self.territories.BALTIC_SEA, self.territories.PRUSSIA, self.territories.BERLIN),
            Move(0, Nations.RUSSIA, self.territories.PRUSSIA, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.CUT)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)

    def test_support_to_hold_on_convoying_unit_allowed(self):
        """
        A unit that is convoying, can receive a hold support.

        Germany:
        A Berlin - Sweden
        F Baltic Sea Convoys A Berlin - Sweden
        F Prussia Supports F Baltic Sea

        Russia:
        F Livonia - Baltic Sea
        F Gulf of Bothnia Supports F Livonia - Baltic Sea

        The Russian move from Livonia to the Baltic Sea fails. The convoy from
        Berlin to Sweden succeeds.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.BALTIC_SEA),
            Fleet(0, Nations.GERMANY, self.territories.PRUSSIA),
            Fleet(0, Nations.RUSSIA, self.territories.LIVONIA),
            Fleet(0, Nations.RUSSIA, self.territories.GULF_OF_BOTHNIA),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.BERLIN, self.territories.SWEDEN, via_convoy=True),
            Convoy(0, Nations.GERMANY, self.territories.BALTIC_SEA, self.territories.BERLIN, self.territories.SWEDEN),
            Support(0, Nations.GERMANY, self.territories.PRUSSIA, self.territories.BALTIC_SEA, self.territories.BALTIC_SEA),
            Move(0, Nations.RUSSIA, self.territories.LIVONIA, self.territories.BALTIC_SEA),
            Support(0, Nations.RUSSIA, self.territories.GULF_OF_BOTHNIA, self.territories.LIVONIA, self.territories.BALTIC_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.LEGAL)
        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(pieces[1].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)

    def test_support_to_hold_on_moving_unit_not_allowed(self):
        """
        A unit that is moving, can not receive a hold support for the situation
        that the move fails.

        Germany:
        F Baltic Sea - Sweden
        F Prussia Supports F Baltic Sea

        Russia:
        F Livonia - Baltic Sea
        F Gulf of Bothnia Supports F Livonia - Baltic Sea
        A Finland - Sweden

        The support of the fleet in Prussia fails. The fleet in Baltic Sea will
        bounce on the Russian army in Finland and will be dislodged by the
        Russian fleet from Livonia when it returns to the Baltic Sea.
        """
        pieces = [
            Fleet(0, Nations.GERMANY, self.territories.BALTIC_SEA),
            Fleet(0, Nations.GERMANY, self.territories.PRUSSIA),
            Fleet(0, Nations.RUSSIA, self.territories.LIVONIA),
            Fleet(0, Nations.RUSSIA, self.territories.GULF_OF_BOTHNIA),
            Army(0, Nations.RUSSIA, self.territories.FINLAND),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.BALTIC_SEA, self.territories.SWEDEN),
            Support(0, Nations.GERMANY, self.territories.PRUSSIA, self.territories.BALTIC_SEA, self.territories.BALTIC_SEA),
            Move(0, Nations.RUSSIA, self.territories.LIVONIA, self.territories.BALTIC_SEA),
            Support(0, Nations.RUSSIA, self.territories.GULF_OF_BOTHNIA, self.territories.LIVONIA, self.territories.BALTIC_SEA),
            Move(0, Nations.RUSSIA, self.territories.FINLAND, self.territories.SWEDEN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[0].dislodged_by, pieces[2])

    def test_failed_convoy_cannot_receive_hold_support(self):
        """
        If a convoy fails because of disruption of the convoy or when the right
        convoy orders are not given, then the army to be convoyed can not
        receive support in hold, since it still tried to move.

        Austria:
        F Ionian Sea Hold
        A Serbia Supports A Albania - Greece
        A Albania - Greece

        Turkey:
        A Greece - Naples
        A Bulgaria Supports A Greece

        There was a possible convoy from Greece to Naples, before the orders
        were made public (via the Ionian Sea). This means that the order of
        Greece to Naples should never be treated as illegal order and be
        changed in a hold order able to receive hold support (see also issue
        VI.A). Therefore, the support in Bulgaria fails and the army in Greece
        is dislodged by the army in Albania.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.IONIAN_SEA),
            Army(0, Nations.AUSTRIA, self.territories.SERBIA),
            Army(0, Nations.AUSTRIA, self.territories.ALBANIA),
            Army(0, Nations.TURKEY, self.territories.GREECE),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
        ]
        orders = [
            Hold(0, Nations.AUSTRIA, self.territories.IONIAN_SEA),
            Support(0, Nations.AUSTRIA, self.territories.SERBIA, self.territories.ALBANIA, self.territories.GREECE),
            Move(0, Nations.AUSTRIA, self.territories.ALBANIA, self.territories.GREECE),
            Move(0, Nations.TURKEY, self.territories.GREECE, self.territories.NAPLES),
            Support(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.GREECE, self.territories.GREECE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)  # given but fails because not move support
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[2])

    def test_support_to_move_on_holding_unit_not_allowed(self):
        """
        A unit that is holding can not receive a support in moving.

        Italy:
        A Venice - Trieste
        A Tyrolia Supports A Venice - Trieste

        Austria:
        A Albania Supports A Trieste - Serbia
        A Trieste Hold

        The support of the army in Albania fails and the army in Trieste is
        dislodged by the army from Venice.
        """
        pieces = [
            Army(0, Nations.ITALY, self.territories.VENICE),
            Army(0, Nations.ITALY, self.territories.TYROLIA),
            Army(0, Nations.AUSTRIA, self.territories.ALBANIA),
            Army(0, Nations.AUSTRIA, self.territories.TRIESTE),
        ]
        orders = [
            Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TRIESTE),
            Support(0, Nations.ITALY, self.territories.TYROLIA, self.territories.VENICE, self.territories.TRIESTE),
            Support(0, Nations.AUSTRIA, self.territories.ALBANIA, self.territories.TRIESTE, self.territories.SERBIA),
            Hold(0, Nations.AUSTRIA, self.territories.TRIESTE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[0])

    def test_self_dislodgement_prohibited(self):
        """
        A unit may not dislodge a unit of the same great power.

        Germany:
        A Berlin Hold
        F Kiel - Berlin
        A Munich Supports F Kiel - Berlin

        Move to Berlin fails.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Army(0, Nations.GERMANY, self.territories.MUNICH),
        ]
        orders = [
            Hold(0, Nations.GERMANY, self.territories.BERLIN),
            Move(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN),
            Support(0, Nations.GERMANY, self.territories.MUNICH, self.territories.KIEL, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)

    def test_no_self_dislodgement_of_returning_unit(self):
        """
        Idem.

        Germany:
        A Berlin - Prussia
        F Kiel - Berlin
        A Munich Supports F Kiel - Berlin

        Russia:
        A Warsaw - Prussia

        Army in Berlin bounces, but is not dislodged by own unit.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Army(0, Nations.GERMANY, self.territories.MUNICH),
            Army(0, Nations.RUSSIA, self.territories.WARSAW),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.BERLIN, self.territories.PRUSSIA),
            Move(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN),
            Support(0, Nations.GERMANY, self.territories.MUNICH, self.territories.KIEL, self.territories.BERLIN),
            Move(0, Nations.GERMANY, self.territories.WARSAW, self.territories.PRUSSIA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)

    def test_supporting_a_foreign_unit_to_dislodge_own_unit(self):
        """
        You may not help another power in dislodging your own unit.

        Austria:
        F Trieste Hold
        A Vienna Supports A Venice - Trieste

        Italy:
        A Venice - Trieste

        No dislodgment of fleet in Trieste.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.AUSTRIA, self.territories.VIENNA),
            Army(0, Nations.ITALY, self.territories.VENICE),
        ]
        orders = [
            Hold(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Support(0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.VENICE, self.territories.TRIESTE),
            Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TRIESTE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)

    def test_supporting_a_foreign_unit_to_dislodge_returning_own_unit(self):
        """
        Idem.

        Austria:
        F Trieste - Adriatic Sea
        A Vienna Supports A Venice - Trieste

        Italy:
        A Venice - Trieste
        F Apulia - Adriatic Sea

        No dislodgement of fleet in Trieste.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.AUSTRIA, self.territories.VIENNA),
            Army(0, Nations.ITALY, self.territories.VENICE),
            Fleet(0, Nations.ITALY, self.territories.APULIA),
        ]
        orders = [
            Move(0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.ADRIATIC_SEA),
            Support(0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.VENICE, self.territories.TRIESTE),
            Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TRIESTE),
            Move(0, Nations.ITALY, self.territories.APULIA, self.territories.ADRIATIC_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)

    def test_supporting_a_foreign_unit_does_not_prevent_dislodgement(self):
        """
        If a foreign unit has enough support to dislodge your unit, you may not
        prevent that dislodgement by supporting the attack.

        Austria:
        F Trieste Hold
        A Vienna Supports A Venice - Trieste

        Italy:
        A Venice - Trieste
        A Tyrolia Supports A Venice - Trieste
        F Adriatic Sea Supports A Venice - Trieste

        The fleet in Trieste is dislodged.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.AUSTRIA, self.territories.VIENNA),
            Army(0, Nations.ITALY, self.territories.VENICE),
            Army(0, Nations.ITALY, self.territories.TYROLIA),
            Fleet(0, Nations.ITALY, self.territories.ADRIATIC_SEA),
        ]
        orders = [
            Hold(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Support(0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.VENICE, self.territories.TRIESTE),
            Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TRIESTE),
            Support(0, Nations.ITALY, self.territories.TYROLIA, self.territories.VENICE, self.territories.TRIESTE),
            Support(0, Nations.ITALY, self.territories.ADRIATIC_SEA, self.territories.VENICE, self.territories.TRIESTE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)

    def test_defender_cannot_cut_support_for_attack_on_itself(self):
        """
        A unit that is attacked by a supported unit can not prevent
        dislodgement by guessing which of the units will do the support.

        Russia:
        F Constantinople Supports F Black Sea - Ankara
        F Black Sea - Ankara

        Turkey:
        F Ankara - Constantinople

        The support of Constantinople is not cut and the fleet in Ankara is
        dislodged by the fleet in the Black Sea. a name="6.D.16">
        """
        pieces = [
            Fleet(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE),
            Fleet(0, Nations.RUSSIA, self.territories.BLACK_SEA),
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
        ]
        orders = [
            Support(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE, self.territories.BLACK_SEA, self.territories.ANKARA),
            Move(0, Nations.RUSSIA, self.territories.BLACK_SEA, self.territories.ANKARA),
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.DISLODGED)

    def test_convoying_a_unit_dislodging_a_unit_of_the_same_power_is_allowed(self):
        """
        It is allowed to convoy a foreign unit that dislodges your own unit.

        England:
        A London Hold
        F North Sea Convoys A Belgium - London

        France:
        F English Channel Supports A Belgium - London
        A Belgium - London

        The English army in London is dislodged by the French army coming from
        Belgium.
        """
        pieces = [
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Fleet(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
            Army(0, Nations.FRANCE, self.territories.BELGIUM),
        ]
        orders = [
            Hold(0, Nations.ENGLAND, self.territories.LONDON),
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.BELGIUM, self.territories.LONDON),
            Support(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.BELGIUM, self.territories.LONDON),
            Move(0, Nations.FRANCE, self.territories.BELGIUM, self.territories.LONDON, via_convoy=True),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[0].dislodged_by, pieces[3])
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.MOVES)

    def test_dislodgement_cuts_support(self):
        """
        The famous dislodge rule.

        Russia:
        F Constantinople Supports F Black Sea - Ankara
        F Black Sea - Ankara

        Turkey:
        F Ankara - Constantinople
        A Smyrna Supports F Ankara - Constantinople
        A Armenia - Ankara

        The Russian fleet in Constantinople is dislodged. This cuts the support
        to from Black Sea to Ankara. Black Sea will bounce with the army from
        Armenia.
        """
        pieces = [
            Fleet(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE),
            Fleet(0, Nations.RUSSIA, self.territories.BLACK_SEA),
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.SMYRNA),
            Army(0, Nations.TURKEY, self.territories.ARMENIA),
        ]
        orders = [
            Support(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE, self.territories.BLACK_SEA, self.territories.ANKARA),
            Move(0, Nations.RUSSIA, self.territories.BLACK_SEA, self.territories.ANKARA),
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Support(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.ARMENIA, self.territories.ANKARA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[0].support_decision, Outcomes.CUT)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)

    def test_surviving_unit_will_sustain_support(self):
        """
        Idem. But now with an additional hold that prevents dislodgement.

        Russia:
        F Constantinople Supports F Black Sea - Ankara
        F Black Sea - Ankara
        A Bulgaria Supports F Constantinople

        Turkey:
        F Ankara - Constantinople
        A Smyrna Supports F Ankara - Constantinople
        A Armenia - Ankara

        The Russian fleet in the Black Sea will dislodge the Turkish fleet in
        Ankara.
        """
        pieces = [
            Fleet(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE),
            Fleet(0, Nations.RUSSIA, self.territories.BLACK_SEA),
            Army(0, Nations.RUSSIA, self.territories.BULGARIA),
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.SMYRNA),
            Army(0, Nations.TURKEY, self.territories.ARMENIA),
        ]
        orders = [
            Support(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE, self.territories.BLACK_SEA, self.territories.ANKARA),
            Move(0, Nations.RUSSIA, self.territories.BLACK_SEA, self.territories.ANKARA),
            Support(0, Nations.RUSSIA, self.territories.BULGARIA, self.territories.CONSTANTINOPLE, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Support(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.ARMENIA, self.territories.ANKARA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[1])

    def test_even_when_surviving_is_in_alternative_way(self):
        """
        Now, the dislodgement is prevented because the supports comes from a
        Russian army:

        Russia:
        F Constantinople Supports F Black Sea - Ankara
        F Black Sea - Ankara
        A Smyrna Supports F Ankara - Constantinople

        Turkey:
        F Ankara - Constantinople

        The Russian fleet in Constantinople is not dislodged, because one of
        the support is of Russian origin. The support from Black Sea to Ankara
        will sustain and the fleet in Ankara will be dislodged.
        """
        pieces = [
            Fleet(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE),
            Fleet(0, Nations.RUSSIA, self.territories.BLACK_SEA),
            Army(0, Nations.RUSSIA, self.territories.SMYRNA),
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
        ]
        orders = [
            Support(0, Nations.RUSSIA, self.territories.CONSTANTINOPLE, self.territories.BLACK_SEA, self.territories.ANKARA),
            Move(0, Nations.RUSSIA, self.territories.BLACK_SEA, self.territories.ANKARA),
            Support(0, Nations.RUSSIA, self.territories.SMYRNA, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[1])

    def test_unit_cannot_cut_support_of_its_own_country(self):
        """
        Although this is not mentioned in all rulebooks, it is generally
        accepted that when a unit attacks another unit of the same Great Power,
        it will not cut support.

        England:
        F London Supports F North Sea - English Channel
        F North Sea - English Channel
        A Yorkshire - London

        France:
        F English Channel Hold

        The army in York does not cut support. This means that the fleet in the
        English Channel is dislodged by the fleet in the North Sea.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.YORKSHIRE),
            Fleet(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
        ]
        orders = [
            Support(0, Nations.ENGLAND, self.territories.LONDON, self.territories.NORTH_SEA, self.territories.ENGLISH_CHANNEL),
            Move(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.ENGLISH_CHANNEL),
            Move(0, Nations.ENGLAND, self.territories.YORKSHIRE, self.territories.LONDON),
            Hold(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[1])

    def test_dislodging_does_not_cancel_a_support_cut(self):
        """
        Sometimes there is the question whether a dislodged moving unit does
        not cut support (similar to the dislodge rule). This is not the case.

        Austria:
        F Trieste Hold

        Italy:
        A Venice - Trieste
        A Tyrolia Supports A Venice - Trieste

        Germany:
        A Munich - Tyrolia

        Russia:
        A Silesia - Munich
        A Berlin Supports A Silesia - Munich

        Although the German army is dislodged, it still cuts the Italian
        support. That means that the Austrian Fleet is not dislodged.
        """
        pieces = [
            Fleet(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.ITALY, self.territories.VENICE),
            Army(0, Nations.ITALY, self.territories.TYROLIA),
            Army(0, Nations.GERMANY, self.territories.MUNICH),
            Army(0, Nations.RUSSIA, self.territories.SILESIA),
            Army(0, Nations.RUSSIA, self.territories.BERLIN),
        ]
        orders = [
            Hold(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Move(0, Nations.ITALY, self.territories.VENICE, self.territories.TRIESTE),
            Support(0, Nations.ITALY, self.territories.TYROLIA, self.territories.VENICE, self.territories.TRIESTE),
            Move(0, Nations.GERMANY, self.territories.MUNICH, self.territories.TYROLIA),
            Move(0, Nations.RUSSIA, self.territories.SILESIA, self.territories.MUNICH),
            Support(0, Nations.RUSSIA, self.territories.BERLIN, self.territories.SILESIA, self.territories.MUNICH),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.CUT)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[5].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[4])

    def test_impossible_fleet_move_cannot_be_supported(self):
        """
        If a fleet tries moves to a land area it seems pointless to support the
        fleet, since the move will fail anyway. However, in such case, the
        support is also invalid for defense purposes.

        Germany:
        F Kiel - Munich
        A Burgundy Supports F Kiel - Munich

        Russia:
        A Munich - Kiel
        A Berlin Supports A Munich - Kiel

        The German move from Kiel to Munich is illegal (fleets can not go to
        Munich). Therefore, the support from Burgundy fails and the Russian
        army in Munich will dislodge the fleet in Kiel. Note that the failing
        of the support is not explicitly mentioned in the rulebooks (the DPTG
        is more clear about this point). If you take the rulebooks very
        literally, you might conclude that the fleet in Munich is not
        dislodged, but this is an incorrect interpretation.
        """
        pieces = [
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Army(0, Nations.GERMANY, self.territories.BURGUNDY),
            Army(0, Nations.RUSSIA, self.territories.MUNICH),
            Army(0, Nations.RUSSIA, self.territories.BERLIN),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.KIEL, self.territories.MUNICH),
            Support(0, Nations.GERMANY, self.territories.BURGUNDY, self.territories.KIEL, self.territories.MUNICH),
            Move(0, Nations.RUSSIA, self.territories.MUNICH, self.territories.KIEL),
            Support(0, Nations.RUSSIA, self.territories.BERLIN, self.territories.MUNICH, self.territories.KIEL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[0].dislodged_by, pieces[2])
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)

    def test_impossible_coast_move_cannot_be_supported(self):
        """
        Comparable with the previous test case, but now the fleet move is
        impossible for coastal reasons.

        Italy:
        F Gulf of Lyon - Spain(sc)
        F Western Mediterranean Supports F Gulf of Lyon - Spain(sc)

        France:
        F Spain(nc) - Gulf of Lyon
        F Marseilles Supports F Spain(nc) - Gulf of Lyon

        The French move from Spain North Coast to Gulf of Lyon is illegal
        (wrong coast). Therefore, the support from Marseilles fails and the
        fleet in Spain is dislodged.
        """
        pieces = [
            Fleet(0, Nations.ITALY, self.territories.GULF_OF_LYON),
            Fleet(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN),
            Fleet(0, Nations.FRANCE, self.territories.SPAIN, self.named_coasts.SPAIN_NC),
            Fleet(0, Nations.FRANCE, self.territories.MARSEILLES),
        ]
        orders = [
            Move(0, Nations.ITALY, self.territories.GULF_OF_LYON, self.territories.SPAIN, self.named_coasts.SPAIN_SC),
            Support(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN, self.territories.GULF_OF_LYON, self.territories.SPAIN),
            Move(0, Nations.FRANCE, self.territories.SPAIN, self.territories.GULF_OF_LYON),
            Support(0, Nations.FRANCE, self.territories.MARSEILLES, self.territories.SPAIN, self.territories.GULF_OF_LYON),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)

    def test_impossible_army_move_cannot_be_supported(self):
        """
        Comparable with the previous test case, but now an army tries to move
        into sea and the support is used in a beleaguered garrison.

        France:
        A Marseilles - Gulf of Lyon
        F Spain(sc) Supports A Marseilles - Gulf of Lyon

        Italy:
        F Gulf of Lyon Hold

        Turkey:
        F Tyrrhenian Sea Supports F Western Mediterranean - Gulf of Lyon
        F Western Mediterranean - Gulf of Lyon

        The French move from Marseilles to Gulf of Lyon is illegal (an army can
        not go to sea). Therefore, the support from Spain fails and there is no
        beleaguered garrison. The fleet in the Gulf of Lyon is dislodged by the
        Turkish fleet in the Western Mediterranean.
        """
        pieces = [
            Army(0, Nations.FRANCE, self.territories.MARSEILLES),
            Fleet(0, Nations.FRANCE, self.territories.SPAIN, self.named_coasts.SPAIN_NC),
            Fleet(0, Nations.ITALY, self.territories.GULF_OF_LYON),
            Fleet(0, Nations.TURKEY, self.territories.WESTERN_MEDITERRANEAN),
            Fleet(0, Nations.TURKEY, self.territories.TYRRHENIAN_SEA),
        ]
        orders = [
            Move(0, Nations.FRANCE, self.territories.MARSEILLES, self.territories.GULF_OF_LYON),
            Support(0, Nations.FRANCE, self.territories.SPAIN,  self.territories.MARSEILLES, self.territories.GULF_OF_LYON),
            Hold(0, Nations.ITALY, self.territories.GULF_OF_LYON),
            Move(0, Nations.TURKEY, self.territories.WESTERN_MEDITERRANEAN, self.territories.GULF_OF_LYON),
            Support(0, Nations.TURKEY, self.territories.TYRRHENIAN_SEA, self.territories.WESTERN_MEDITERRANEAN, self.territories.GULF_OF_LYON),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[2].dislodged_by, pieces[3])
        self.assertEqual(orders[3].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)

    def test_failing_hold_support_can_be_supported(self):
        """
        If an adjudicator fails on one of the previous three test cases, then
        the bug should be removed with care. A failing move can not be
        supported, but a failing hold support, because of some preconditions
        (unmatching order) can still be supported.

        Germany:
        A Berlin Supports A Prussia
        F Kiel Supports A Berlin

        Russia:
        F Baltic Sea Supports A Prussia - Berlin
        A Prussia - Berlin

        Although the support of Berlin on Prussia fails (because of unmatching
        orders), the support of Kiel on Berlin is still valid. So, Berlin will
        not be dislodged.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Fleet(0, Nations.RUSSIA, self.territories.BALTIC_SEA),
            Fleet(0, Nations.RUSSIA, self.territories.PRUSSIA),
        ]
        orders = [
            Support(0, Nations.GERMANY, self.territories.BERLIN, self.territories.PRUSSIA, self.territories.PRUSSIA),
            Support(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN, self.territories.BERLIN),
            Support(0, Nations.RUSSIA, self.territories.BALTIC_SEA, self.territories.PRUSSIA, self.territories.BERLIN),
            Move(0, Nations.RUSSIA, self.territories.PRUSSIA, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.CUT)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)

    def test_failing_move_support_can_be_supported(self):
        """
        Similar as the previous test case, but now with an unmatched support to
        move.

        Germany:
        A Berlin Supports A Prussia - Silesia
        F Kiel Supports A Berlin

        Russia:
        F Baltic Sea Supports A Prussia - Berlin
        A Prussia - Berlin

        Again, Berlin will not be dislodged.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.GERMANY, self.territories.KIEL),
            Fleet(0, Nations.RUSSIA, self.territories.BALTIC_SEA),
            Fleet(0, Nations.RUSSIA, self.territories.PRUSSIA),
        ]
        orders = [
            Support(0, Nations.GERMANY, self.territories.BERLIN, self.territories.PRUSSIA, self.territories.SILESIA),
            Support(0, Nations.GERMANY, self.territories.KIEL, self.territories.BERLIN, self.territories.BERLIN),
            Support(0, Nations.RUSSIA, self.territories.BALTIC_SEA, self.territories.PRUSSIA, self.territories.BERLIN),
            Move(0, Nations.RUSSIA, self.territories.PRUSSIA, self.territories.BERLIN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.CUT)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)

    def test_failing_convoy_can_be_supported(self):
        """
        Similar as the previous test case, but now with an unmatched convoy.

        England:
        F Sweden - Baltic Sea
        F Denmark Supports F Sweden - Baltic Sea

        Germany:
        A Berlin Hold

        Russia:
        F Baltic Sea Convoys A Berlin - Livonia
        F Prussia Supports F Baltic Sea

        The convoy order in the Baltic Sea is unmatched and fails. However, the
        support of Prussia on the Baltic Sea is still valid and the fleet in
        the Baltic Sea is not dislodged.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.SWEDEN),
            Fleet(0, Nations.ENGLAND, self.territories.DENMARK),
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Fleet(0, Nations.RUSSIA, self.territories.BALTIC_SEA),
            Fleet(0, Nations.RUSSIA, self.territories.PRUSSIA),
        ]
        orders = [
            Move(0, Nations.ENGLAND, self.territories.SWEDEN, self.territories.BALTIC_SEA),
            Support(0, Nations.ENGLAND, self.territories.DENMARK, self.territories.SWEDEN, self.territories.BALTIC_SEA),
            Hold(0, Nations.GERMANY, self.territories.BERLIN),
            Convoy(0, Nations.RUSSIA, self.territories.BALTIC_SEA, self.territories.BERLIN, self.territories.LIVONIA),
            Support(0, Nations.RUSSIA, self.territories.PRUSSIA, self.territories.BALTIC_SEA, self.territories.BALTIC_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)

    def test_impossible_move_and_support(self):
        """
        If a move is impossible then it can be treated as "illegal", which
        makes a hold support possible.

        Austria:
        A Budapest Supports F Rumania

        Russia:
        F Rumania - Holland

        Turkey:
        F Black Sea - Rumania
        A Bulgaria Supports F Black Sea - Rumania

        The move of the Russian fleet is impossible. But the question is,
        whether it is "illegal" (see issue 4.E.1). If the move is "illegal" it
        must be ignored and that makes the hold support of the army in Budapest
        valid and the fleet in Rumania will not be dislodged.

        I prefer that the move is "illegal", which means that the fleet in the
        Black Sea does not dislodge the supported Russian fleet.
        """
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.BUDAPEST),
            Fleet(0, Nations.RUSSIA, self.territories.RUMANIA),
            Fleet(0, Nations.TURKEY, self.territories.BLACK_SEA),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
        ]
        orders = [
            Support(0, Nations.AUSTRIA, self.territories.BUDAPEST, self.territories.RUMANIA, self.territories.RUMANIA),
            Move(0, Nations.RUSSIA, self.territories.RUMANIA, self.territories.HOLLAND),
            Move(0, Nations.TURKEY, self.territories.BLACK_SEA, self.territories.RUMANIA),
            Support(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.BLACK_SEA, self.territories.RUMANIA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)

    def test_move_to_impossible_coast_and_support(self):
        """
        Similar to the previous test case, but now the move can be "illegal"
        because of the wrong coast.

        Austria:
        A Budapest Supports F Rumania

        Russia:
        F Rumania - Bulgaria(sc)

        Turkey:
        F Black Sea - Rumania
        A Bulgaria Supports F Black Sea - Rumania

        Again the move of the Russian fleet is impossible. However, some people
        might correct the coast (see issue 4.B.3). If the coast is not
        corrected, again the question is whether it is "illegal" (see issue
        4.E.1). If the move is "illegal" it must be ignored and that makes the
        hold support of the army in Budapest valid and the fleet in Rumania
        will not be dislodged.

        I prefer that unambiguous orders are not changed and that the move is
        "illegal". That means that the fleet in the Black Sea does not dislodge
        the supported Russian fleet.
        """
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.BUDAPEST),
            Fleet(0, Nations.RUSSIA, self.territories.RUMANIA),
            Fleet(0, Nations.TURKEY, self.territories.BLACK_SEA),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
        ]
        orders = [
            Support(0, Nations.AUSTRIA, self.territories.BUDAPEST, self.territories.RUMANIA, self.territories.RUMANIA),
            Move(0, Nations.RUSSIA, self.territories.RUMANIA, self.territories.BULGARIA, self.named_coasts.BULGARIA_SC),
            Move(0, Nations.TURKEY, self.territories.BLACK_SEA, self.territories.RUMANIA),
            Support(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.BLACK_SEA, self.territories.RUMANIA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)

    def test_unwanted_support_allowed(self):
        """
        A self stand-off can be broken by an unwanted support.

        Austria:
        A Serbia - Budapest
        A Vienna - Budapest

        Russia:
        A Galicia Supports A Serbia - Budapest

        Turkey:
        A Bulgaria - Serbia

        Due to the Russian support, the army in Serbia advances to Budapest.
        This enables Turkey to capture Serbia with the army in Bulgaria.
        """
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.SERBIA),
            Army(0, Nations.AUSTRIA, self.territories.VIENNA),
            Army(0, Nations.RUSSIA, self.territories.GALICIA),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
        ]
        orders = [
            Move(0, Nations.AUSTRIA, self.territories.SERBIA, self.territories.BUDAPEST),
            Move(0, Nations.AUSTRIA, self.territories.VIENNA, self.territories.BUDAPEST),
            Support(0, Nations.RUSSIA, self.territories.GALICIA, self.territories.SERBIA, self.territories.BUDAPEST),
            Move(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.SERBIA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.MOVES)

    def test_support_targeting_own_area_not_allowed(self):
        """
        Support targeting the area where the supporting unit is standing, is
        illegal.

        Germany:
        A Berlin - Prussia
        A Silesia Supports A Berlin - Prussia
        F Baltic Sea Supports A Berlin - Prussia

        Italy:
        A Prussia Supports Livonia - Prussia

        Russia:
        A Warsaw Supports A Livonia - Prussia
        A Livonia - Prussia

        Russia and Italy wanted to get rid of the Italian army in Prussia (to
        build an Italian fleet somewhere else). However, they didn't want a
        possible German attack on Prussia to succeed. They invented this odd
        order of Italy. It was intended that the attack of the army in Livonia
        would have strength three, so it would be capable to prevent the
        possible German attack to succeed. However, the order of Italy is
        illegal, because a unit may only support to an area where the unit can
        go by itself. A unit can't go to the area it is already standing, so
        the Italian order is illegal and the German move from Berlin succeeds.
        Even if it would be legal, the German move from Berlin would still
        succeed, because the support of Prussia is cut by Livonia and Berlin.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
            Army(0, Nations.GERMANY, self.territories.SILESIA),
            Fleet(0, Nations.GERMANY, self.territories.BALTIC_SEA),
            Army(0, Nations.ITALY, self.territories.PRUSSIA),
            Army(0, Nations.RUSSIA, self.territories.WARSAW),
            Army(0, Nations.RUSSIA, self.territories.LIVONIA),
        ]
        orders = [
            Move(0, Nations.GERMANY, self.territories.BERLIN, self.territories.PRUSSIA),
            Support(0, Nations.GERMANY, self.territories.SILESIA, self.territories.BERLIN, self.territories.PRUSSIA),
            Support(0, Nations.GERMANY, self.territories.BALTIC_SEA, self.territories.BERLIN, self.territories.PRUSSIA),
            Support(0, Nations.ITALY, self.territories.PRUSSIA, self.territories.LIVONIA, self.territories.PRUSSIA),
            Support(0, Nations.RUSSIA, self.territories.WARSAW, self.territories.LIVONIA, self.territories.PRUSSIA),
            Move(0, Nations.RUSSIA, self.territories.LIVONIA, self.territories.PRUSSIA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[3].dislodged_by, pieces[0])
