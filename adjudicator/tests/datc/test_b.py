import unittest

from adjudicator import illegal_messages
from adjudicator.decisions import Outcomes
from adjudicator.order import Build, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestCoastalIssues(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_moving_with_unspecified_coast_when_coast_necessary(self):
        """
        Coast is significant in this case:

        France:
        F Portugal - Spain

        Some adjudicators take a default coast (see issue 4.B.1).

        I prefer that the move fails.
        """
        fleet = Fleet(0, Nations.FRANCE, self.territories.PORTUGAL)
        order = Move(0, Nations.FRANCE, self.territories.PORTUGAL, self.territories.SPAIN)

        self.state.register(fleet, order)

        with self.assertRaises(ValueError):
            process(self.state)

    def test_moving_with_unspecified_coast_when_coast_unnecessary(self):
        """
        There is only one coast possible in this case:

        France:
        F Gascony - Spain

        Since the North Coast is the only coast that can be reached, it seems
        logical that the a move is attempted to the north coast of Spain. Some
        adjudicators require that a coast is also specified in this case and
        will decide that the move fails or take a default coast (see issue
        4.B.2).

        I prefer that an attempt is made to the only possible coast, the north
        coast of Spain.
        """
        fleet = Fleet(0, Nations.FRANCE, self.territories.GASCONY)
        order = Move(0, Nations.FRANCE, self.territories.GASCONY, self.territories.SPAIN)
        self.state.register(fleet, order)

        with self.assertRaises(ValueError):
            process(self.state)

    def test_moving_with_wrong_coast_when_coast_is_not_necessary(self):
        """
        If only one coast is possible, but the wrong coast can be specified.

        France:
        F Gascony - Spain(sc)

        If the rules are played very clemently, a move will be attempted to the
        north coast of Spain. However, since this order is very clear and
        precise, it is more common that the move fails (see issue 4.B.3).

        I prefer that the move fails.
        """
        fleet = Fleet(0, Nations.FRANCE, self.territories.GASCONY)
        order = Move(0, Nations.FRANCE, self.territories.GASCONY, self.territories.SPAIN, self.named_coasts.SPAIN_SC)

        self.state.register(fleet, order)
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.M007)

    def test_support_to_unreachable_coast_allowed(self):
        """
        A fleet can give support to a coast where it can not go.

        France:
        F Gascony - Spain(nc)
        F Marseilles Supports F Gascony - Spain(nc)

        Italy:
        F Western Mediterranean - Spain(sc)

        Although the fleet in Marseilles can not go to the north coast it can
        still support targeting the north coast. So, the support is successful,
        the move of the fleet in Gascony succeeds and the move of the Italian
        fleet fails.
        """
        pieces = [
            Fleet(0, Nations.FRANCE, self.territories.GASCONY),
            Fleet(0, Nations.FRANCE, self.territories.MARSEILLES),
            Fleet(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN)
        ]

        fleet_gascony_move = Move(0, Nations.FRANCE, self.territories.GASCONY, self.territories.SPAIN, self.named_coasts.SPAIN_NC)
        fleet_marseilles_support = Support(0, Nations.FRANCE, self.territories.MARSEILLES, self.territories.GASCONY, self.territories.SPAIN)
        fleet_western_med_move = Move(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN, self.territories.SPAIN, self.named_coasts.SPAIN_SC)

        self.state.register(*pieces, fleet_gascony_move, fleet_marseilles_support, fleet_western_med_move)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(fleet_gascony_move.move_decision, Outcomes.MOVES)
        self.assertEqual(fleet_western_med_move.move_decision, Outcomes.FAILS)
        self.assertEqual(fleet_marseilles_support.support_decision, Outcomes.GIVEN)

    def test_support_from_unreachable_coast_not_allowed(self):
        """
        A fleet can not give support to an area that can not be reached from
        the current coast of the fleet.

        France:
        F Marseilles - Gulf of Lyon
        F Spain(nc) Supports F Marseilles - Gulf of Lyon

        Italy:
        F Gulf of Lyon Hold

        The Gulf of Lyon can not be reached from the North Coast of Spain.
        Therefore, the support of Spain is invalid and the fleet in the Gulf of
        Lyon is not dislodged.
        """
        pieces = [
            Fleet(0, Nations.FRANCE, self.territories.MARSEILLES),
            Fleet(0, Nations.FRANCE, self.territories.SPAIN, self.named_coasts.SPAIN_NC),
            Fleet(0, Nations.ITALY, self.territories.GULF_OF_LYON)
        ]

        fleet_marseilles_move = Move(0, Nations.FRANCE, self.territories.MARSEILLES, self.territories.GULF_OF_LYON)
        fleet_spain_nc_support = Support(0, Nations.FRANCE, self.territories.SPAIN, self.territories.MARSEILLES, self.territories.GULF_OF_LYON)
        fleet_gol_hold = Hold(0, Nations.ITALY, self.territories.GULF_OF_LYON)

        self.state.register(*pieces, fleet_marseilles_move, fleet_spain_nc_support, fleet_gol_hold)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(fleet_spain_nc_support.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(fleet_spain_nc_support.illegal_message, illegal_messages.S002)
        self.assertEqual(fleet_marseilles_move.move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.SUSTAINS)

    def test_support_can_be_cut_with_other_coast(self):
        """
        Support can be cut from the other coast.

        England:
        F Irish Sea Supports F North Atlantic Ocean - Mid-Atlantic Ocean
        F North Atlantic Ocean - Mid-Atlantic Ocean

        France:
        F Spain(nc) Supports F Mid-Atlantic Ocean
        F Mid-Atlantic Ocean Hold

        Italy:
        F Gulf of Lyon - Spain(sc)

        The Italian fleet in the Gulf of Lyon will cut the support in Spain.
        That means that the French fleet in the Mid Atlantic Ocean will be
        dislodged by the English fleet in the North Atlantic Ocean.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_ATLANTIC),
            Fleet(0, Nations.ENGLAND, self.territories.IRISH_SEA),
            Fleet(0, Nations.FRANCE, self.territories.SPAIN, self.named_coasts.SPAIN_NC),
            Fleet(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
            Fleet(0, Nations.ITALY, self.territories.GULF_OF_LYON),
        ]
        orders = [
            Move(0, Nations.ENGLAND, self.territories.NORTH_ATLANTIC, self.territories.MID_ATLANTIC),
            Support(0, Nations.ENGLAND, self.territories.IRISH_SEA, self.territories.NORTH_ATLANTIC, self.territories.MID_ATLANTIC),
            Support(0, Nations.FRANCE, self.territories.SPAIN, self.territories.MID_ATLANTIC, self.territories.MID_ATLANTIC),
            Hold(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
            Move(0, Nations.ITALY, self.territories.GULF_OF_LYON, self.territories.SPAIN, self.named_coasts.SPAIN_SC),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[2].support_decision, Outcomes.CUT)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)

    def test_supporting_with_unspecified_coast(self):
        """
        Most house rules accept support orders without coast specification.

        France:
        F Portugal Supports F Mid-Atlantic Ocean - Spain
        F Mid-Atlantic Ocean - Spain(nc)

        Italy:
        F Gulf of Lyon Supports F Western Mediterranean - Spain(sc)
        F Western Mediterranean - Spain(sc)

        See issue 4.B.4. If coasts are not required in support orders, then the
        support of Portugal is successful. This means that the Italian fleet in
        the Western Mediterranean bounces. Some adjudicators may not accept a
        support order without coast (the support will fail or a default coast
        is taken). In that case the support order of Portugal fails (in case of
        a default coast the coast will probably the south coast) and the
        Italian fleet in the Western Mediterranean will successfully move.

        I prefer that the support succeeds and the Italian fleet in the Western
        Mediterranean bounces.
        """
        pieces = [
            Fleet(0, Nations.FRANCE, self.territories.PORTUGAL),
            Fleet(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
            Fleet(0, Nations.ITALY, self.territories.GULF_OF_LYON),
            Fleet(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN),
        ]
        orders = [
            Support(0, Nations.FRANCE, self.territories.PORTUGAL, self.territories.MID_ATLANTIC, self.territories.SPAIN),
            Move(0, Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.SPAIN, self.named_coasts.SPAIN_NC),
            Support(0, Nations.ITALY, self.territories.GULF_OF_LYON, self.territories.WESTERN_MEDITERRANEAN, self.territories.SPAIN),
            Move(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN, self.territories.SPAIN, self.named_coasts.SPAIN_SC),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)

    def test_supporting_with_unspecified_coast_when_only_one_coast_is_possible(self):
        """
        Some hardliners require a coast in a support order even when only one
        coast is possible.

        France:
        F Portugal Supports F Gascony - Spain
        F Gascony - Spain(nc)

        Italy:
        F Gulf of Lyon Supports F Western Mediterranean - Spain(sc)
        F Western Mediterranean - Spain(sc)

        See issue 4.B.4. If coasts are not required in support orders, then the
        support of Portugal is successful. This means that the Italian fleet in
        the Western Mediterranean bounces. Some adjudicators may not accept a
        support order without coast (the support will fail or a default coast
        is taken). In that case the support order of Portugal fails
        (in case of a default coast the coast will probably the south coast)
        and the Italian fleet in the Western Mediterranean will successfully
        move.

        I prefer that supporting without coasts should be allowed. So I prefer
        that the support of Portugal is successful and that the Italian fleet
        in the Western Mediterranean bounces.
        """
        pieces = [
            Fleet(0, Nations.FRANCE, self.territories.PORTUGAL),
            Fleet(0, Nations.FRANCE, self.territories.GASCONY),
            Fleet(0, Nations.ITALY, self.territories.GULF_OF_LYON),
            Fleet(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN),
        ]
        orders = [
            Support(0, Nations.FRANCE, self.territories.PORTUGAL, self.territories.GASCONY, self.territories.SPAIN),
            Move(0, Nations.FRANCE, self.territories.GASCONY, self.territories.SPAIN, self.named_coasts.SPAIN_NC),
            Support(0, Nations.ITALY, self.territories.GULF_OF_LYON, self.territories.WESTERN_MEDITERRANEAN, self.territories.SPAIN),
            Move(0, Nations.ITALY, self.territories.WESTERN_MEDITERRANEAN, self.territories.SPAIN, self.named_coasts.SPAIN_SC),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)

    def test_coast_cannot_be_ordered_to_change(self):
        """
        The coast can not change by just ordering the other coast.

        France has a fleet on the north coast of Spain and orders:

        France:
        F Spain(sc) - Gulf of Lyon

        The move fails.
        """
        # Not really relevant because can't specify source coast
        fleet = Fleet(0, Nations.FRANCE, self.territories.SPAIN, self.named_coasts.SPAIN_NC)
        move = Move(0, Nations.FRANCE, self.territories.SPAIN, self.territories.SPAIN, self.named_coasts.SPAIN_SC)

        self.state.register(fleet, move)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(move.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(move.illegal_message, illegal_messages.M002)

    def test_army_movement_with_coastal_specification(self):
        """
        For armies the coasts are irrelevant:

        France:
        A Gascony - Spain(nc)

        If only perfect orders are accepted, then the move will fail. But it is
        also possible that coasts are ignored in this case and a move will be
        attempted (see issue 4.B.6).

        I prefer that a move will be attempted.
        """
        army = Army(0, Nations.FRANCE, self.territories.GASCONY)
        move = Move(0, Nations.FRANCE, self.territories.GASCONY, self.territories.SPAIN, self.named_coasts.SPAIN_NC)

        self.state.register(army, move)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(move.move_decision, Outcomes.MOVES)
        self.assertEqual(move.legal_decision, Outcomes.LEGAL)

    def test_coastal_crawl_not_allowed(self):
        """
        If a fleet is leaving a sector from a certain coast while in the
        opposite direction another fleet is moving to another coast of the
        sector, it is still a head to head battle. This has been decided in the
        great revision of the 1961 rules that resulted in the 1971 rules.

        Turkey:
        F Bulgaria(sc) - Constantinople
        F Constantinople - Bulgaria(ec)

        Both moves fail.
        """
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.BULGARIA, self.named_coasts.BULGARIA_SC),
            Fleet(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.BULGARIA, self.named_coasts.BULGARIA_EC),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)

    def test_building_with_unspecified_coast(self):
        """
        Coast must be specified in certain build cases:

        Russia:
        Build F St Petersburg
        If no default coast is taken (see issue 4.B.7), the build fails.

        I do not like default coast, so I prefer that the build fails.
        """
        order = Build(0, Nations.RUSSIA, self.territories.ST_PETERSBURG, 'fleet')

        self.state.register(order)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(order.legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(order.illegal_message, illegal_messages.B006)
