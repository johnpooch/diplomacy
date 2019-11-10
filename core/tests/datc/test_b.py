from core import models
from core.utils.command import build, convoy, hold, move, support
from core.utils.piece import army, fleet
from core.models.base import PieceType
from core.tests.base import HelperMixin, TerritoriesMixin
from core.tests.base import InitialGameStateTestCase as TestCase


class TestCoastalIssues(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['user.json', 'game.json', 'turn.json', 'nations.json',
                'territories.json', 'territory_states.json',
                'named_coasts.json', 'supply_centers.json']

    def setUp(self):
        self.game = models.Game.objects.get()
        self.turn = models.Turn.objects.get()
        self.initialise_territories()
        self.initialise_named_coasts()
        self.initialise_nations()
        self.initialise_orders()

    def test_moving_with_unspecified_coast_when_coast_necessary(self):
        """
        Coast is significant in this case:

        France:
        F Portugal - Spain

        Some adjudicators take a default coast (see issue 4.B.1).

        I prefer that the move fails.
        """
        fleet_portugal = fleet(self.turn, self.france, self.portugal)

        fleet_portugal_move = move(
            self.france_order, fleet_portugal, self.portugal, self.spain
        )

        fleet_portugal_move.check_illegal()
        self.assertTrue(fleet_portugal_move.illegal)
        self.assertEqual(
            fleet_portugal_move.illegal_message,
            ('Cannot order an fleet into a territory with named coasts '
             'without specifying a named coast.')
        )

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
        fleet_gascony = fleet(self.turn, self.france, self.gascony)

        fleet_gascony_move = move(
            self.france_order, fleet_gascony, self.gascony, self.spain
        )

        fleet_gascony_move.check_illegal()
        self.assertFalse(fleet_gascony_move.illegal)

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
        fleet_gascony = fleet(self.turn, self.france, self.gascony)

        fleet_gascony_move = move(
            self.france_order, fleet_gascony, self.gascony, self.spain,
            self.spain_sc
        )

        fleet_gascony_move.check_illegal()
        self.assertTrue(fleet_gascony_move.illegal)
        self.assertEqual(
            fleet_gascony_move.illegal_message,
            'Fleet Gascony cannot reach Spain (sc).'
        )

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
        the move of the fleet in Gasgony succeeds and the move of the Italian
        fleet fails.
        """
        fleet_gascony = fleet(self.turn, self.france, self.gascony)
        fleet_marseilles = fleet(self.turn, self.france, self.marseilles)
        fleet_western_med = fleet(self.turn, self.italy, self.western_mediterranean)

        fleet_gascony_move = move(
            self.france_order, fleet_gascony, self.gascony, self.spain,
            self.spain_nc
        )
        fleet_marseilles_support = support(
            self.france_order, fleet_marseilles, self.marseilles, self.gascony,
            self.spain
        )
        fleet_western_med_move = move(
            self.italy_order, fleet_western_med, self.western_mediterranean,
            self.spain, self.spain_sc
        )

        models.Command.objects.process()
        [c.refresh_from_db() for c in (fleet_gascony_move,
                                       fleet_western_med_move, fleet_marseilles_support)]

        self.assertTrue(fleet_gascony_move.succeeds)

        self.assertTrue(fleet_western_med_move.fails)
        self.assertFalse(fleet_western_med.dislodged)

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
        fleet_marseilles = fleet(self.turn, self.france, self.marseilles)
        fleet_spain_nc = fleet(self.turn, self.france, self.spain, self.spain_nc)
        fleet_gol = fleet(self.turn, self.italy, self.gulf_of_lyon)

        fleet_marseilles_move = move(
            self.france_order, fleet_marseilles, self.marseilles,
            self.gulf_of_lyon,
        )
        fleet_spain_nc_support = support(
            self.france_order, fleet_spain_nc, self.spain, self.marseilles,
            self.gulf_of_lyon
        )
        fleet_gol_hold = hold(
            self.italy_order, fleet_gol, self.gulf_of_lyon,
        )

        models.Command.objects.process()
        [c.refresh_from_db() for c in (fleet_marseilles_move,
                                       fleet_spain_nc_support, fleet_gol)]

        self.assertTrue(fleet_spain_nc_support.illegal)
        self.assertEqual(
            fleet_spain_nc_support.illegal_message,
            'Fleet Spain (nc) cannot reach Gulf Of Lyon.'
        )
        self.assertTrue(fleet_marseilles_move.fails)
        self.assertFalse(fleet_gol.dislodged)

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
        fleet_irish_sea = fleet(self.turn, self.england, self.irish_sea)
        fleet_north_atlantic = fleet(self.turn, self.england, self.north_atlantic)

        fleet_spain_nc = fleet(self.turn, self.france, self.spain, self.spain_nc)
        fleet_mid_atlantic = fleet(self.turn, self.france, self.mid_atlantic)

        fleet_gol = fleet(self.turn, self.italy, self.gulf_of_lyon)

        fleet_irish_sea_support = support(
            self.england_order, fleet_irish_sea, self.irish_sea,
            self.north_atlantic, self.mid_atlantic
        )
        fleet_north_atlantic_move = move(
            self.england_order, fleet_north_atlantic, self.north_atlantic,
            self.mid_atlantic,
        )
        fleet_spain_nc_support = support(
            self.france_order, fleet_spain_nc, self.spain, self.mid_atlantic, self.mid_atlantic
        )
        fleet_mid_atlantic_hold = hold(
            self.france_order, fleet_mid_atlantic, self.mid_atlantic
        )
        fleet_gol_move = move(
            self.italy_order, fleet_gol, self.gulf_of_lyon, self.spain,
            self.spain_sc
        )

        models.Command.objects.process()
        [c.refresh_from_db() for c in (fleet_mid_atlantic, fleet_spain_nc_support)]

        self.assertEqual(fleet_mid_atlantic.dislodged_by, fleet_north_atlantic)

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
        fleet_portugal = fleet(self.turn, self.france, self.portugal)
        fleet_mid_atlantic = fleet(self.turn, self.france, self.mid_atlantic)

        fleet_gol = fleet(self.turn, self.italy, self.gulf_of_lyon)
        fleet_western_med = fleet(self.turn, self.italy, self.western_mediterranean)

        fleet_portugal_support = support(
            self.france_order, fleet_portugal, self.portugal,
            self.mid_atlantic, self.spain
        )
        fleet_mid_atlantic_move = move(
            self.france_order, fleet_mid_atlantic, self.mid_atlantic,
            self.spain, self.spain_nc
        )
        fleet_gol_support = support(
            self.italy_order, fleet_gol, self.gulf_of_lyon,
            self.western_mediterranean, self.spain
        )
        fleet_western_med_move = move(
            self.italy_order, fleet_western_med, self.western_mediterranean,
            self.spain, self.spain_sc
        )

        models.Command.objects.process()
        [c.refresh_from_db() for c in (fleet_western_med,
                                       fleet_western_med_move,
                                       fleet_portugal_support)]

        self.assertTrue(fleet_western_med_move.fails)
        self.assertFalse(fleet_western_med.dislodged)

        self.assertTrue(fleet_portugal_support.succeeds)

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
        fleet_portugal = fleet(self.turn, self.france, self.portugal)
        fleet_gascony = fleet(self.turn, self.france, self.gascony)

        fleet_gol = fleet(self.turn, self.italy, self.gulf_of_lyon)
        fleet_western_med = fleet(self.turn, self.italy, self.western_mediterranean)

        fleet_portugal_support = support(
            self.france_order, fleet_portugal, self.portugal,
            self.gascony, self.spain
        )
        move(
            self.france_order, fleet_gascony, self.gascony,
            self.spain, self.spain_nc
        )
        support(
            self.italy_order, fleet_gol, self.gulf_of_lyon,
            self.western_mediterranean, self.spain
        )
        fleet_western_med_move = move(
            self.italy_order, fleet_western_med, self.western_mediterranean,
            self.spain, self.spain_sc
        )

        models.Command.objects.process()
        [c.refresh_from_db() for c in (fleet_western_med,
                                       fleet_western_med_move,
                                       fleet_portugal_support)]

        self.assertTrue(fleet_western_med_move.fails)
        self.assertFalse(fleet_western_med.dislodged)

        self.assertTrue(fleet_portugal_support.succeeds)

    def test_supporting_with_wrong_coast(self):
        """
        Coasts can be specified in a support, but the result depends on the house rules.

        France:
        F Portugal Supports F Mid-Atlantic Ocean - Spain(nc)
        F Mid-Atlantic Ocean - Spain(sc)

        Italy:
        F Gulf of Lyon Supports F Western Mediterranean - Spain(sc)
        F Western Mediterranean - Spain(sc)

        See issue 4.B.4. If it is required that the coast matches, then the
        support of the French fleet in the Mid-Atlantic Ocean fails and that
        the Italian fleet in the Western Mediterranean moves successfully. Some
        adjudicators ignores the coasts in support orders. In that case, the
        move of the Italian fleet bounces.

        I prefer that the support fails and that the Italian fleet in the
        Western Mediterranean moves successfully.
        """
        # This is not relevant because specifying a coast for a support command
        # is not possible in this implementation
        pass

    def test_unit_ordered_with_wrong_coast(self):
        """
        A player might specify the wrong coast for the ordered unit.

        France has a fleet on the south coast of Spain and orders:

        France:
        F Spain(nc) - Gulf of Lyon

        If only perfect orders are accepted, then the move will fail, but since
        the coast for the ordered unit has no purpose, it might also be ignored
        (see issue 4.B.5).

        I prefer that a move will be attempted.
        """
        # This is not relevant because specifying the souce coast for a move
        # command is not possible in this implementation
        pass

    def test_coast_cannot_be_ordered_to_change(self):
        """
        The coast can not change by just ordering the other coast.

        France has a fleet on the north coast of Spain and orders:

        France:
        F Spain(sc) - Gulf of Lyon

        The move fails.
        """
        # Not really relevant because can't specify source coast
        fleet_spain_nc = fleet(self.turn, self.france, self.spain, self.spain_nc)
        command = move(self.france_order, fleet_spain_nc, self.spain,
                       self.gulf_of_lyon)
        command.check_illegal()
        self.assertTrue(command.illegal)
        self.assertEqual(
            command.illegal_message,
            'Fleet Spain (nc) cannot reach Gulf Of Lyon.'
        )

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
        # In this implementation, an attempt to create a command for an army
        # which specifies target coast will raise an exception. This basically
        # satisfies the datc requirement.
        army_gascony = army(self.turn, self.france, self.gascony)
        with self.assertRaises(ValueError):
            move(self.france_order, army_gascony, self.gascony, self.spain,
                 self.spain_nc)

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
        fleet_bulgaria_ec = fleet(self.turn, self.turkey, self.bulgaria, self.bulgaria_ec)
        fleet_constantinople = fleet(self.turn, self.turkey, self.constantinople)

        fleet_bulgaria_ec_move = move(self.turkey_order, fleet_bulgaria_ec,
                                      self.bulgaria, self.constantinople)
        fleet_constantinople_move = move(self.turkey_order,
                                         fleet_constantinople,
                                         self.constantinople, self.bulgaria,
                                         self.bulgaria_ec)

        models.Command.objects.process()
        [c.refresh_from_db() for c in (fleet_bulgaria_ec_move,
                                       fleet_constantinople_move)]

        self.assertTrue(fleet_bulgaria_ec_move.fails)
        self.assertTrue(fleet_constantinople_move.fails)

    def test_building_with_unspecified_coast(self):
        """
        Coast must be specified in certain build cases:

        Russia:
        Build F St Petersburg
        If no default coast is taken (see issue 4.B.7), the build fails.

        I do not like default coast, so I prefer that the build fails.
        """
        command = build(
            self.russia_order,
            PieceType.FLEET,
            self.st_petersburg,
        )
        command.check_illegal()
        self.assertTrue(command.illegal)
        self.assertEqual(
            command.illegal_message,
            ('Must specify a coast when building a fleet in a '
             'territory with named coasts.')
        )
