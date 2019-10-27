from core import models
from core.utils.command import build, convoy, hold, move, support
from core.utils.piece import army, fleet
from core.models.base import PieceType
from core.tests.base import HelperMixin, TerritoriesMixin
from core.tests.base import InitialGameStateTestCase as TestCase


class TestSupportsAndDislodges(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'supply_centers.json']

    # NOTE these should be moved to a class setup method.
    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.initialise_named_coasts()
        self.initialise_nations()
        self.initialise_orders()

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
        fleet_adriatic = fleet(self.austria, self.adriatic_sea)
        army_trieste = army(self.austria, self.trieste)

        army_venice = army(self.italy, self.venice)
        army_tyrolia = army(self.italy, self.tyrolia)

        fleet_adriatic_support = support(
            self.austria_order, fleet_adriatic, self.adriatic_sea,
            self.trieste, self.venice,
        )
        army_trieste_move = move(
            self.austria_order, army_trieste, self.trieste, self.venice,
        )
        army_venice_hold = hold(
            self.italy_order, army_venice, self.venice,
        )
        army_tyrolia_support = support(
            self.italy_order, army_tyrolia, self.tyrolia, self.venice,
            self.venice,
        )
        commands = [fleet_adriatic_support, army_trieste_move,
                    army_venice_hold, army_tyrolia_support]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_adriatic_support.succeeds)
        self.assertTrue(army_trieste_move.fails)
        self.assertTrue(army_venice_hold.succeeds)
        self.assertTrue(army_tyrolia_support.succeeds)

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
        fleet_adriatic = fleet(self.austria, self.adriatic_sea)
        army_trieste = army(self.austria, self.trieste)
        army_vienna = army(self.austria, self.vienna)

        army_venice = army(self.italy, self.venice)
        army_tyrolia = army(self.italy, self.tyrolia)

        fleet_adriatic_support = support(
            self.austria_order, fleet_adriatic, self.adriatic_sea,
            self.trieste, self.venice,
        )
        army_trieste_move = move(
            self.austria_order, army_trieste, self.trieste, self.venice,
        )
        army_vienna_move = move(
            self.austria_order, army_vienna, self.vienna, self.tyrolia,
        )
        army_venice_hold = hold(
            self.italy_order, army_venice, self.venice,
        )
        army_tyrolia_support = support(
            self.italy_order, army_tyrolia, self.tyrolia, self.venice,
            self.venice,
        )
        commands = [fleet_adriatic_support, army_trieste_move, army_vienna_move,
                    army_venice_hold, army_tyrolia_support, army_venice]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_adriatic_support.succeeds)
        self.assertTrue(army_trieste_move.succeeds)
        self.assertTrue(army_vienna_move.fails)
        self.assertTrue(army_venice_hold.fails)
        self.assertTrue(army_venice.dislodged)
        self.assertTrue(army_tyrolia_support.fails)

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
        fleet_adriatic = fleet(self.austria, self.adriatic_sea)
        army_trieste = army(self.austria, self.trieste)

        army_venice = army(self.italy, self.venice)
        fleet_ionian = fleet(self.italy, self.ionian_sea)

        fleet_adriatic_support = support(
            self.austria_order, fleet_adriatic, self.adriatic_sea,
            self.trieste, self.venice,
        )
        army_trieste_move = move(
            self.austria_order, army_trieste, self.trieste, self.venice,
        )
        army_venice_hold = hold(
            self.italy_order, army_venice, self.venice,
        )
        fleet_ionian_move = move(
            self.italy_order, fleet_ionian, self.ionian_sea, self.adriatic_sea,
        )
        commands = [fleet_adriatic_support, army_trieste_move,
                    army_venice_hold, fleet_ionian_move, army_venice]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_adriatic_support.fails)
        self.assertTrue(fleet_adriatic_support.cut)

        self.assertTrue(army_trieste_move.fails)
        self.assertTrue(fleet_ionian_move.fails)

        self.assertTrue(army_venice_hold.succeeds)

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
        army_berlin = army(self.germany, self.berlin)
        army_kiel = army(self.germany, self.kiel)

        fleet_baltic = army(self.russia, self.baltic_sea)
        army_prussia = army(self.russia, self.prussia)

        army_berlin_support = support(
            self.germany_order, army_berlin, self.berlin, self.kiel, self.kiel
        )
        army_kiel_support = support(
            self.germany_order, army_kiel, self.kiel, self.berlin, self.berlin
        )
        fleet_baltic_support = support(
            self.russia_order, fleet_baltic, self.baltic_sea, self.prussia,
            self.berlin
        )
        army_prussia_move = move(
            self.russia_order, army_prussia, self.prussia, self.berlin
        )

        commands = [army_berlin, army_berlin_support, army_kiel_support,
                    fleet_baltic_support, army_prussia_move]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_berlin_support.fails)
        self.assertTrue(army_berlin_support.cut)
        self.assertTrue(army_berlin.sustains)

        self.assertTrue(army_kiel_support.succeeds)

        self.assertTrue(fleet_baltic_support.succeeds)
        self.assertTrue(army_prussia_move.fails)

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
        army_berlin = army(self.germany, self.berlin)
        army_kiel = army(self.germany, self.kiel)
        army_munich = army(self.germany, self.munich)

        fleet_baltic = army(self.russia, self.baltic_sea)
        army_prussia = army(self.russia, self.prussia)

        army_berlin_support = support(
            self.germany_order, army_berlin, self.berlin, self.munich,
            self.silesia
        )
        army_kiel_support = support(
            self.germany_order, army_kiel, self.kiel, self.berlin, self.berlin
        )
        army_munich_move = move(
            self.germany_order, army_munich, self.munich, self.silesia
        )
        fleet_baltic_support = support(
            self.russia_order, fleet_baltic, self.baltic_sea, self.prussia,
            self.berlin
        )
        army_prussia_move = move(
            self.russia_order, army_prussia, self.prussia, self.berlin
        )

        commands = [army_berlin, army_berlin_support, army_kiel_support,
                    army_munich_move, fleet_baltic_support, army_prussia_move]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_berlin_support.fails)
        self.assertTrue(army_berlin_support.cut)
        self.assertTrue(army_berlin.sustains)

        self.assertTrue(army_munich_move.succeeds)

        self.assertTrue(army_kiel_support.succeeds)

        self.assertTrue(fleet_baltic_support.succeeds)
        self.assertTrue(army_prussia_move.fails)

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
        army_berlin = army(self.germany, self.berlin)
        fleet_baltic = fleet(self.germany, self.baltic_sea)
        fleet_prussia = fleet(self.germany, self.prussia)

        fleet_livonia = army(self.russia, self.livonia)
        fleet_gulf_of_bothnia = army(self.russia, self.gulf_of_bothnia)

        army_berlin_move = move(
            self.germany_order, army_berlin, self.berlin, self.sweden,
        )
        fleet_baltic_convoy = convoy(
            self.germany_order, fleet_baltic, self.baltic_sea, self.berlin,
            self.sweden
        )
        fleet_prussia_support = support(
            self.germany_order, fleet_prussia, self.prussia, self.baltic_sea,
            self.baltic_sea
        )
        fleet_livonia_move = move(
            self.russia_order, fleet_livonia, self.livonia, self.baltic_sea
        )
        fleet_gulf_of_bothnia_support = support(
            self.russia_order, fleet_gulf_of_bothnia, self.gulf_of_bothnia,
            self.livonia, self.baltic_sea
        )

        commands = [army_berlin_move, fleet_baltic_convoy,
                    fleet_prussia_support, fleet_livonia_move,
                    fleet_gulf_of_bothnia_support]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_livonia_move.fails)

        self.assertTrue(fleet_baltic_convoy.piece.sustains)
        self.assertTrue(fleet_baltic_convoy.succeeds)

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
        fleet_baltic = fleet(self.germany, self.baltic_sea)
        fleet_prussia = fleet(self.germany, self.prussia)

        fleet_livonia = fleet(self.russia, self.livonia)
        fleet_gulf_of_bothnia = fleet(self.russia, self.gulf_of_bothnia)
        army_finland = army(self.russia, self.finland)

        fleet_baltic_move = move(
            self.germany_order, fleet_baltic, self.baltic_sea, self.sweden,
        )
        fleet_prussia_support = support(
            self.germany_order, fleet_prussia, self.prussia, self.baltic_sea,
            self.baltic_sea
        )
        fleet_livonia_move = move(
            self.russia_order, fleet_livonia, self.livonia, self.baltic_sea
        )
        fleet_gulf_of_bothnia_support = support(
            self.russia_order, fleet_gulf_of_bothnia, self.gulf_of_bothnia,
            self.livonia, self.baltic_sea
        )
        army_finland_move = move(
            self.russia_order, army_finland, self.finland, self.sweden
        )

        commands = [fleet_baltic_move, fleet_prussia_support, fleet_prussia,
                    fleet_livonia_move, fleet_gulf_of_bothnia_support,
                    army_finland_move]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_gulf_of_bothnia_support.succeeds)
        self.assertTrue(fleet_prussia_support.fails)
        self.assertTrue(fleet_baltic_move.fails)
        self.assertTrue(fleet_baltic_move.piece.dislodged)
        self.assertTrue(army_finland_move.fails)

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
        fleet_ionian = fleet(self.austria, self.ionian_sea)
        army_serbia = army(self.austria, self.serbia)
        army_albania = army(self.austria, self.albania)

        army_greece = army(self.turkey, self.greece)
        army_bulgaria = army(self.turkey, self.bulgaria)

        fleet_ionian_hold = hold(
            self.austria_order, fleet_ionian, self.ionian_sea
        )
        army_serbia_support = support(
            self.austria_order, army_serbia, self.serbia, self.albania,
            self.greece,
        )
        army_albania_move = move(
            self.austria_order, army_albania, self.albania, self.greece
        )
        army_greece_move = move(
            self.turkey_order, army_greece, self.greece, self.naples
        )
        army_bulgaria_support = support(
            self.turkey_order, army_bulgaria, self.bulgaria, self.greece,
            self.greece
        )

        commands = [fleet_ionian_hold, army_albania_move, army_greece_move,
                    army_greece, army_serbia_support, army_bulgaria_support]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_bulgaria_support.fails)
        self.assertTrue(army_serbia_support.succeeds)
        self.assertTrue(army_albania_move.succeeds)
        self.assertTrue(army_greece_move.fails)
        self.assertTrue(army_greece.dislodged)

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
        army_venice = army(self.italy, self.venice)
        army_tyrolia = army(self.italy, self.tyrolia)

        army_albania = army(self.austria, self.albania)
        army_trieste = army(self.austria, self.trieste)

        army_venice_move = move(self.italy_order, army_venice, self.venice,
                                self.trieste)
        army_tyrolia_support = support(self.italy_order, army_tyrolia,
                                       self.tyrolia, self.venice, self.trieste)

        army_albania_support = support(self.austria_order, army_albania,
                                       self.albania, self.trieste, self.serbia)
        army_trieste_hold = hold(self.austria_order, army_trieste,
                                 self.trieste)

        commands = [army_venice_move, army_tyrolia_support,
                    army_albania_support, army_trieste_hold, army_trieste]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_albania_support.fails)
        self.assertTrue(army_trieste_hold.fails)
        self.assertTrue(army_trieste.dislodged)
        self.assertEqual(
            army_trieste.dislodged_by,
            army_venice
        )
        self.assertTrue(army_tyrolia_support.succeeds)
        self.assertTrue(army_venice_move.succeeds)

    def test_self_dislodgment_prohibited(self):
        """
        A unit may not dislodge a unit of the same great power.

        Germany:
        A Berlin Hold
        F Kiel - Berlin
        A Munich Supports F Kiel - Berlin

        Move to Berlin fails.
        """
        army_berlin = army(self.germany, self.berlin)
        fleet_kiel = fleet(self.germany, self.kiel)
        army_munich = army(self.germany, self.munich)

        army_berlin_hold = hold(self.germany_order, army_berlin, self.berlin)
        fleet_kiel_move = move(self.germany_order, fleet_kiel, self.kiel,
                               self.berlin)
        army_munich_support = support(self.germany_order, army_munich,
                                      self.munich, self.kiel, self.berlin)

        commands = [army_berlin_hold, fleet_kiel_move,
                    army_munich_support]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_kiel_move.fails)
        self.assertTrue(army_berlin_hold.succeeds)
        self.assertTrue(army_munich_support.succeeds)

    def test_no_self_dislodgment_of_returning_unit(self):
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
        army_berlin = army(self.germany, self.berlin)
        fleet_kiel = fleet(self.germany, self.kiel)
        army_munich = army(self.germany, self.munich)

        army_warsaw = army(self.russia, self.warsaw)

        army_berlin_move = move(self.germany_order, army_berlin, self.berlin,
                                self.prussia)
        fleet_kiel_move = move(self.germany_order, fleet_kiel, self.kiel,
                               self.berlin)
        army_munich_support = support(self.germany_order, army_munich,
                                      self.munich, self.kiel, self.berlin)

        army_warsaw_move = move(self.russia_order, army_warsaw, self.warsaw,
                                self.prussia)

        commands = [army_berlin, army_berlin_move, fleet_kiel_move,
                    army_munich_support, army_warsaw_move]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_kiel_move.fails)
        self.assertTrue(army_berlin_move.fails)
        self.assertTrue(army_berlin.sustains)
        self.assertTrue(army_munich_support.succeeds)
        self.assertTrue(army_warsaw_move.fails)

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
        fleet_trieste = fleet(self.austria, self.trieste)
        army_vienna = army(self.austria, self.vienna)

        army_venice = army(self.italy, self.venice)

        fleet_trieste_hold = hold(self.austria_order, fleet_trieste,
                                  self.trieste)
        army_vienna_support = support(self.austria_order, army_vienna,
                                      self.vienna, self.venice, self.trieste)

        army_venice_move = move(self.italy_order, army_venice, self.venice,
                                self.trieste)

        commands = [fleet_trieste_hold, army_vienna_support, army_venice_move]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_trieste_hold.succeeds)
        self.assertTrue(army_vienna_support.succeeds)
        self.assertTrue(army_venice_move.fails)

    def test_supporting_a_foreign_unit_to_dislodge_returning_own_unit(self):
        """
        Idem.

        Austria:
        F Trieste - Adriatic Sea
        A Vienna Supports A Venice - Trieste

        Italy:
        A Venice - Trieste
        F Apulia - Adriatic Sea

        No dislodgment of fleet in Trieste.
        """
        fleet_trieste = fleet(self.austria, self.trieste)
        army_vienna = army(self.austria, self.vienna)

        army_venice = army(self.italy, self.venice)
        fleet_apulia = fleet(self.italy, self.apulia)

        fleet_trieste_move = move(self.austria_order, fleet_trieste,
                                  self.trieste, self.adriatic_sea)
        army_vienna_support = support(self.austria_order, army_vienna,
                                      self.vienna, self.venice, self.trieste)

        army_venice_move = move(self.italy_order, army_venice, self.venice,
                                self.trieste)

        fleet_apulia_move = move(self.italy_order, fleet_apulia, self.apulia,
                                 self.adriatic_sea)

        commands = [fleet_trieste_move, army_vienna_support, army_venice_move,
                    fleet_apulia_move, fleet_trieste]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_trieste_move.fails)
        self.assertTrue(fleet_trieste.sustains)
        self.assertTrue(army_vienna_support.succeeds)
        self.assertTrue(army_venice_move.fails)
        self.assertTrue(fleet_apulia_move.fails)

    def test_supporting_a_foreign_unit_does_not_prevent_dislodgment(self):
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
        fleet_trieste = fleet(self.austria, self.trieste)
        army_vienna = army(self.austria, self.vienna)

        army_venice = army(self.italy, self.venice)
        army_tyrolia = army(self.italy, self.tyrolia)
        fleet_adriatic = fleet(self.italy, self.adriatic_sea)

        fleet_trieste_hold = hold(self.austria_order, fleet_trieste,
                                  self.trieste)
        army_vienna_support = support(self.austria_order, army_vienna,
                                      self.vienna, self.venice, self.trieste)

        army_venice_move = move(self.italy_order, army_venice, self.venice,
                                self.trieste)
        army_tyrolia_support = support(self.italy_order, army_tyrolia,
                                       self.tyrolia, self.venice, self.trieste)
        fleet_adriatic_support = support(self.italy_order, fleet_adriatic,
                                         self.adriatic_sea, self.venice,
                                         self.trieste)

        commands = [fleet_trieste_hold, army_vienna_support, army_venice_move,
                    army_tyrolia_support, fleet_adriatic_support]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_venice_move.succeeds)
        self.assertTrue(army_tyrolia_support.succeeds)
        self.assertTrue(fleet_adriatic_support.succeeds)

        self.assertTrue(army_vienna_support.succeeds)
        self.assertTrue(fleet_trieste_hold.fails)
        self.assertTrue(army_tyrolia_support.succeeds)
        self.assertTrue(fleet_adriatic_support.succeeds)

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
        fleet_constantinople = fleet(self.russia, self.constantinople)
        fleet_black_sea = fleet(self.russia, self.black_sea)

        fleet_ankara = fleet(self.turkey, self.ankara)

        fleet_constantinople_support = support(
            self.russia_order, fleet_constantinople, self.constantinople,
            self.black_sea, self.ankara
        )
        fleet_black_sea_move = move(
            self.russia_order, fleet_black_sea, self.black_sea, self.ankara
        )
        fleet_ankara_move = move(
            self.turkey_order, fleet_ankara, self.ankara, self.constantinople
        )

        commands = [fleet_constantinople_support, fleet_black_sea_move,
                    fleet_ankara_move, fleet_ankara]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_constantinople_support.succeeds)
        self.assertTrue(fleet_black_sea_move.succeeds)
        self.assertTrue(fleet_ankara_move.fails)
        self.assertTrue(fleet_ankara.dislodged)

    def test_convoying_a_unit_dislodging_a_unit_of_the_same_power_is_allowed(self):
        """
        It is allowed to convoy a foreign unit that dislodges your own unit is
        allowed.

        England:
        A London Hold
        F North Sea Convoys A Belgium - London

        France:
        F English Channel Supports A Belgium - London
        A Belgium - London

        The English army in London is dislodged by the French army coming from
        Belgium.
        """
        army_london = army(self.england, self.london)
        fleet_north_sea = fleet(self.england, self.north_sea)

        fleet_english_channel = fleet(self.france, self.english_channel)
        army_belgium = army(self.france, self.belgium)

        army_london_hold = hold(self.england_order, army_london, self.london)
        fleet_north_sea_convoy = convoy(
            self.england_order, fleet_north_sea, self.north_sea, self.belgium,
            self.london
        )
        fleet_english_channel_support = support(
            self.france_order, fleet_english_channel, self.english_channel,
            self.belgium, self.london
        )
        army_belgium_move = move(
            self.france_order, army_belgium, self.belgium, self.london
        )

        commands = [army_london_hold, army_london, fleet_north_sea_convoy,
                    fleet_english_channel_support, army_belgium_move]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_london_hold.fails)
        self.assertTrue(army_london.dislodged)
        self.assertEqual(army_london.dislodged_by, army_belgium)

        self.assertTrue(fleet_english_channel_support.succeeds)

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
        fleet_constantinople = fleet(self.russia, self.constantinople)
        fleet_black_sea = fleet(self.russia, self.black_sea)

        fleet_ankara = fleet(self.turkey, self.ankara)
        army_smyrna = army(self.turkey, self.smyrna)
        army_armenia = army(self.turkey, self.armenia)

        fleet_constantinople_support = support(
            self.russia_order, fleet_constantinople, self.constantinople,
            self.black_sea, self.ankara
        )
        fleet_black_sea_move = move(
            self.russia_order, fleet_black_sea, self.black_sea, self.ankara
        )

        fleet_ankara_move = move(
            self.turkey_order, fleet_ankara, self.ankara, self.constantinople
        )
        army_smyrna_support = support(
            self.turkey_order, army_smyrna, self.smyrna, self.ankara,
            self.constantinople
        )
        army_armenia_move = move(
            self.turkey_order, army_armenia, self.armenia, self.ankara,
        )

        commands = [fleet_constantinople_support, fleet_black_sea_move,
                    fleet_ankara_move, army_smyrna_support, army_armenia_move,
                    fleet_constantinople]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_constantinople_support.fails)
        self.assertTrue(fleet_constantinople.dislodged)

        self.assertTrue(fleet_black_sea_move.fails)
        self.assertTrue(army_armenia_move.fails)

        self.assertTrue(fleet_ankara_move.succeeds)
        self.assertTrue(army_smyrna_support.succeeds)

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
        fleet_constantinople = fleet(self.russia, self.constantinople)
        fleet_black_sea = fleet(self.russia, self.black_sea)
        army_bulgaria = army(self.russia, self.bulgaria)

        fleet_ankara = fleet(self.turkey, self.ankara)
        army_smyrna = army(self.turkey, self.smyrna)
        army_armenia = army(self.turkey, self.armenia)

        fleet_constantinople_support = support(
            self.russia_order, fleet_constantinople, self.constantinople,
            self.black_sea, self.ankara
        )
        fleet_black_sea_move = move(
            self.russia_order, fleet_black_sea, self.black_sea, self.ankara
        )
        army_bulgaria_support = support(
            self.russia_order, army_bulgaria, self.bulgaria,
            self.constantinople, self.constantinople
        )

        fleet_ankara_move = move(
            self.turkey_order, fleet_ankara, self.ankara, self.constantinople
        )
        army_smyrna_support = support(
            self.turkey_order, army_smyrna, self.smyrna, self.ankara,
            self.constantinople
        )
        army_armenia_move = move(
            self.turkey_order, army_armenia, self.armenia, self.ankara,
        )

        commands = [
            fleet_constantinople_support, fleet_black_sea_move,
            fleet_ankara_move, army_smyrna_support, army_armenia_move,
            fleet_constantinople, army_bulgaria_support, fleet_ankara,
            fleet_black_sea
        ]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_constantinople_support.succeeds)
        self.assertTrue(fleet_black_sea_move.succeeds)
        self.assertTrue(army_bulgaria_support.succeeds)

        self.assertTrue(fleet_ankara_move.fails)
        self.assertTrue(fleet_ankara.dislodged)
        self.assertTrue(
            fleet_ankara.dislodged_by,
            fleet_black_sea
        )
        self.assertTrue(army_smyrna_support.succeeds)

        self.assertTrue(army_armenia_move.fails)

    def test_even_when_surviving_is_in_alternative_way(self):
        """
        Now, the dislodgement is prevented because the supports comes from a Russian army:

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
        fleet_constantinople = fleet(self.russia, self.constantinople)
        fleet_black_sea = fleet(self.russia, self.black_sea)
        army_smyrna = army(self.russia, self.smyrna)

        fleet_ankara = fleet(self.turkey, self.ankara)

        fleet_constantinople_support = support(
            self.russia_order, fleet_constantinople, self.constantinople,
            self.black_sea, self.ankara
        )
        fleet_black_sea_move = move(
            self.russia_order, fleet_black_sea, self.black_sea, self.ankara
        )
        army_smyrna_support = support(
            self.russia_order, army_smyrna, self.smyrna,
            self.ankara, self.constantinople
        )

        fleet_ankara_move = move(
            self.turkey_order, fleet_ankara, self.ankara, self.constantinople
        )

        commands = [
            fleet_constantinople_support, fleet_black_sea_move,
            fleet_ankara_move, army_smyrna_support, fleet_constantinople,
            fleet_ankara, fleet_black_sea
        ]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_constantinople_support.succeeds)
        self.assertTrue(fleet_black_sea_move.succeeds)

        self.assertTrue(army_smyrna_support.succeeds)
        self.assertTrue(fleet_ankara_move.fails)
        self.assertTrue(fleet_ankara.dislodged)
        self.assertTrue(
            fleet_ankara.dislodged_by,
            fleet_black_sea
        )

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
        fleet_london = fleet(self.england, self.london)
        fleet_north_sea = fleet(self.england, self.north_sea)
        army_yorkshire = army(self.england, self.yorkshire)

        fleet_english_channel = fleet(self.france, self.english_channel)

        fleet_london_support = support(
            self.england_order, fleet_london, self.london, self.north_sea,
            self.english_channel
        )
        fleet_north_sea_move = move(
            self.england_order, fleet_north_sea, self.north_sea, self.english_channel
        )
        army_yorkshire_move = move(
            self.england_order, army_yorkshire, self.yorkshire, self.london
        )
        fleet_english_channel_hold = hold(
            self.france_order, fleet_english_channel, self.english_channel
        )

        commands = [
            fleet_london_support, fleet_north_sea_move, army_yorkshire_move,
            fleet_english_channel_hold, fleet_english_channel
        ]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_london_support.succeeds)
        self.assertTrue(fleet_north_sea_move.succeeds)
        self.assertTrue(army_yorkshire_move.fails)

        self.assertTrue(fleet_english_channel_hold.fails)
        self.assertTrue(fleet_english_channel.dislodged)
        self.assertTrue(
            fleet_english_channel.dislodged_by,
            army_yorkshire
        )

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
        fleet_trieste = fleet(self.austria, self.trieste)

        army_venice = army(self.italy, self.venice)
        army_tyrolia = army(self.italy, self.tyrolia)

        army_munich = army(self.germany, self.munich)

        army_silesia = army(self.russia, self.silesia)
        army_berlin = army(self.russia, self.berlin)

        fleet_trieste_hold = hold(
            self.austria_order, fleet_trieste, self.trieste
        )
        army_venice_move = move(
            self.italy_order, army_venice, self.venice, self.trieste
        )
        army_tyrolia_support = support(
            self.italy_order, army_tyrolia, self.tyrolia, self.venice, self.trieste
        )
        army_munich_move = move(
            self.germany_order, army_munich, self.munich, self.tyrolia
        )
        army_silesia_move = move(
            self.russia_order, army_silesia, self.silesia, self.munich
        )
        army_berlin_support = support(
            self.russia_order, army_berlin, self.berlin, self.silesia,
            self.munich,
        )

        commands = [
            fleet_trieste_hold, army_venice_move, army_tyrolia_support,
            army_munich_move, army_silesia_move, army_berlin_support,
            fleet_trieste, army_munich
        ]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_trieste.sustains)
        self.assertTrue(army_munich.dislodged)
        self.assertEqual(army_munich.dislodged_by, army_silesia)

        self.assertTrue(army_tyrolia_support.fails)
        self.assertTrue(army_venice_move.fails)

        self.assertTrue(army_silesia_move.succeeds)
        self.assertTrue(army_berlin_support.succeeds)

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
        fleet_kiel = fleet(self.germany, self.kiel)
        army_burgundy = army(self.germany, self.burgundy)
        army_munich = army(self.russia, self.munich)
        army_berlin = army(self.russia, self.berlin)

        fleet_kiel_move = move(
            self.germany_order, fleet_kiel, self.kiel, self.munich
        )
        army_burgundy_support = support(
            self.germany_order, army_burgundy, self.burgundy, self.kiel, self.munich
        )
        army_munich_move = move(
            self.russia_order, army_munich, self.munich, self.kiel
        )
        army_berlin_support = support(
            self.russia_order, army_berlin, self.berlin, self.munich, self.kiel
        )

        commands = [
            fleet_kiel_move, army_burgundy_support, army_munich_move,
            army_berlin_support, fleet_kiel
        ]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_kiel_move.illegal)
        self.assertEqual(
            fleet_kiel_move.illegal_message,
            'Fleet Kiel cannot reach Munich.'
        )

        self.assertTrue(fleet_kiel.dislodged)
        self.assertEqual(fleet_kiel.dislodged_by, army_munich)

        self.assertTrue(army_munich_move.succeeds)
        self.assertTrue(army_berlin_support.succeeds)

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
        fleet_gulf_of_lyon = fleet(self.italy, self.gulf_of_lyon)
        fleet_western_med = fleet(self.italy, self.western_mediterranean)

        fleet_spain_nc = fleet(self.france, self.spain, self.spain_nc)
        fleet_marseilles = fleet(self.france, self.marseilles)

        fleet_gulf_of_lyon_move = move(
            self.italy_order, fleet_gulf_of_lyon, self.gulf_of_lyon,
            self.spain, self.spain_sc
        )
        fleet_western_med_support = support(
            self.italy_order, fleet_western_med, self.western_mediterranean,
            self.gulf_of_lyon, self.spain, self.spain_sc
        )

        fleet_spain_nc_move = move(
            self.france_order, fleet_spain_nc, self.spain, self.gulf_of_lyon
        )
        fleet_marseilles_support = support(
            self.france_order, fleet_marseilles, self.marseilles,
            self.spain, self.gulf_of_lyon
        )

        commands = [
            fleet_gulf_of_lyon, fleet_gulf_of_lyon_move,
            fleet_western_med_support, fleet_spain_nc_move,
            fleet_marseilles_support, fleet_spain_nc
        ]

        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_spain_nc_move.illegal)
        self.assertEqual(
            fleet_spain_nc_move.illegal_message,
            'Fleet Spain (nc) cannot reach Gulf Of Lyon.'
        )

        self.assertTrue(fleet_gulf_of_lyon_move.succeeds)
        self.assertTrue(fleet_western_med_support.succeeds)

        self.assertTrue(fleet_spain_nc.dislodged)
        self.assertEqual(fleet_spain_nc.dislodged_by, fleet_gulf_of_lyon)

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
        army_marseilles = army(self.france, self.marseilles)
        fleet_spain_sc = fleet(self.france, self.spain, self.spain_sc)

        fleet_gulf_of_lyon = fleet(self.italy, self.gulf_of_lyon)

        fleet_tyrrhenian_sea = fleet(self.turkey, self.tyrrhenian_sea)
        fleet_western_med = fleet(self.turkey, self.western_mediterranean)

        army_marseilles_move = move(
            self.france_order, army_marseilles, self.marseilles,
            self.gulf_of_lyon
        )
        fleet_spain_sc_support = support(
            self.france_order, fleet_spain_sc, self.spain, self.marseilles,
            self.gulf_of_lyon
        )

        fleet_gulf_of_lyon_hold = hold(
            self.italy_order, fleet_gulf_of_lyon, self.gulf_of_lyon,
        )

        fleet_tyrrhenian_sea_support = support(
            self.turkey_order, fleet_tyrrhenian_sea, self.tyrrhenian_sea,
            self.western_mediterranean, self.gulf_of_lyon
        )
        fleet_western_med_move = move(
            self.turkey_order, fleet_western_med, self.western_mediterranean,
            self.gulf_of_lyon
        )

        commands = [
            army_marseilles_move, fleet_spain_sc_support,
            fleet_gulf_of_lyon_hold, fleet_tyrrhenian_sea_support,
            fleet_western_med_move, fleet_gulf_of_lyon
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_marseilles_move.illegal)
        self.assertEqual(
            army_marseilles_move.illegal_message,
            'Army Marseilles cannot reach Gulf Of Lyon.'
        )

        self.assertTrue(fleet_tyrrhenian_sea_support.succeeds)
        self.assertTrue(fleet_western_med_move.succeeds)

        self.assertTrue(fleet_gulf_of_lyon.dislodged)
        self.assertEqual(fleet_gulf_of_lyon.dislodged_by, fleet_western_med)

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
        army_berlin = army(self.germany, self.berlin)
        fleet_kiel = fleet(self.germany, self.kiel)

        fleet_baltic = fleet(self.russia, self.baltic_sea)
        army_prussia = army(self.russia, self.prussia)

        army_berlin_support = support(
            self.germany_order, army_berlin, self.berlin, self.prussia,
            self.prussia
        )
        fleet_kiel_support = support(
            self.germany_order, fleet_kiel, self.kiel, self.berlin,
            self.berlin
        )
        fleet_baltic_support = support(
            self.russia_order, fleet_baltic, self.baltic_sea, self.prussia,
            self.berlin,
        )
        army_prussia_move = move(
            self.russia_order, army_prussia, self.prussia, self.berlin,
        )

        commands = [
            army_berlin_support, fleet_kiel_support,
            fleet_baltic_support, army_prussia_move, army_berlin
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_berlin_support.fails)
        self.assertTrue(fleet_kiel_support.succeeds)

        self.assertTrue(fleet_baltic_support.succeeds)
        self.assertTrue(army_prussia_move.fails)

        self.assertTrue(army_berlin.sustains)

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
        army_berlin = army(self.germany, self.berlin)
        fleet_kiel = fleet(self.germany, self.kiel)

        fleet_baltic = fleet(self.russia, self.baltic_sea)
        army_prussia = army(self.russia, self.prussia)

        army_berlin_support = support(
            self.germany_order, army_berlin, self.berlin, self.prussia,
            self.silesia
        )
        fleet_kiel_support = support(
            self.germany_order, fleet_kiel, self.kiel, self.berlin,
            self.berlin
        )
        fleet_baltic_support = support(
            self.russia_order, fleet_baltic, self.baltic_sea, self.prussia,
            self.berlin,
        )
        army_prussia_move = move(
            self.russia_order, army_prussia, self.prussia, self.berlin,
        )

        commands = [
            army_berlin_support, fleet_kiel_support,
            fleet_baltic_support, army_prussia_move, army_berlin
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_berlin_support.fails)
        self.assertTrue(fleet_kiel_support.succeeds)

        self.assertTrue(fleet_baltic_support.succeeds)
        self.assertTrue(army_prussia_move.fails)

        self.assertTrue(army_berlin.sustains)

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
        fleet_sweden = fleet(self.england, self.sweden)
        fleet_denmark = fleet(self.england, self.denmark)

        army_berlin = army(self.germany, self.berlin)

        fleet_baltic = fleet(self.russia, self.baltic_sea)
        fleet_prussia = fleet(self.russia, self.prussia)

        fleet_sweden_move = move(
            self.england_order, fleet_sweden, self.sweden, self.baltic_sea
        )
        fleet_denmark_support = support(
            self.england_order, fleet_denmark, self.denmark, self.sweden,
            self.baltic_sea
        )
        army_berlin_hold = hold(
            self.germany_order, army_berlin, self.berlin
        )
        fleet_baltic_convoy = convoy(
            self.russia_order, fleet_baltic, self.baltic_sea, self.berlin,
            self.livonia,
        )
        fleet_prussia_support = support(
            self.russia_order, fleet_prussia, self.prussia, self.baltic_sea,
            self.baltic_sea,
        )

        commands = [
            fleet_sweden_move, fleet_denmark_support, fleet_baltic_convoy,
            army_berlin_hold, fleet_prussia_support, fleet_baltic
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_baltic_convoy.fails)
        self.assertTrue(fleet_prussia_support.succeeds)

        self.assertTrue(fleet_baltic.sustains)

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
        army_budapest = army(self.austria, self.budapest)

        fleet_rumania = fleet(self.russia, self.rumania)

        fleet_black_sea = fleet(self.turkey, self.black_sea)
        army_bulgaria = army(self.turkey, self.bulgaria)

        army_budapest_support = support(
            self.austria_order, army_budapest, self.budapest, self.rumania,
            self.rumania
        )
        fleet_rumania_move = move(
            self.russia_order, fleet_rumania, self.rumania, self.holland
        )
        fleet_black_sea_move = move(
            self.turkey_order, fleet_black_sea, self.black_sea, self.rumania
        )
        army_bulgaria_support = support(
            self.turkey_order, army_bulgaria, self.bulgaria, self.black_sea,
            self.rumania
        )

        commands = [
            army_budapest_support, fleet_rumania_move, fleet_black_sea_move,
            army_bulgaria_support, fleet_rumania
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_rumania_move.illegal)
        self.assertTrue(army_budapest_support.succeeds)
        self.assertTrue(fleet_rumania_move.fails)
        self.assertTrue(fleet_rumania.sustains)

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
        army_budapest = army(self.austria, self.budapest)

        fleet_rumania = fleet(self.russia, self.rumania)

        fleet_black_sea = fleet(self.turkey, self.black_sea)
        army_bulgaria = army(self.turkey, self.bulgaria)

        army_budapest_support = support(
            self.austria_order, army_budapest, self.budapest, self.rumania,
            self.rumania
        )
        fleet_rumania_move = move(
            self.russia_order, fleet_rumania, self.rumania, self.bulgaria,
            self.bulgaria_sc
        )
        fleet_black_sea_move = move(
            self.turkey_order, fleet_black_sea, self.black_sea, self.rumania
        )
        army_bulgaria_support = support(
            self.turkey_order, army_bulgaria, self.bulgaria, self.black_sea,
            self.rumania
        )

        commands = [
            army_budapest_support, fleet_rumania_move, fleet_black_sea_move,
            army_bulgaria_support, fleet_rumania
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(fleet_rumania_move.illegal)
        self.assertTrue(army_budapest_support.succeeds)
        self.assertTrue(fleet_rumania_move.fails)
        self.assertTrue(fleet_rumania.sustains)

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
        army_serbia = army(self.austria, self.serbia)
        army_vienna = army(self.austria, self.vienna)

        army_galicia = army(self.russia, self.galicia)

        army_bulgaria = army(self.turkey, self.bulgaria)

        army_serbia_move = move(
            self.austria_order, army_serbia, self.serbia, self.budapest
        )
        army_vienna_move = move(
            self.austria_order, army_vienna, self.vienna, self.budapest
        )
        army_galicia_support = support(
            self.russia_order, army_galicia, self.galicia, self.serbia,
            self.budapest
        )
        army_bulgaria_move = move(
            self.turkey_order, army_bulgaria, self.bulgaria, self.serbia,
        )

        commands = [
            army_serbia_move, army_vienna_move, army_galicia_support,
            army_bulgaria_move,
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_serbia_move.succeeds)
        self.assertTrue(army_galicia_support.succeeds)

        self.assertTrue(army_vienna_move.fails)
        self.assertTrue(army_bulgaria_move.succeeds)

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
        army_berlin = army(self.germany, self.berlin)
        army_silesia = army(self.germany, self.silesia)
        fleet_baltic = fleet(self.germany, self.baltic_sea)

        army_prussia = army(self.italy, self.prussia)

        army_warsaw = army(self.russia, self.warsaw)
        army_livonia = army(self.russia, self.livonia)

        army_berlin_move = move(
            self.germany_order, army_berlin, self.berlin, self.prussia
        )
        army_silesia_support = support(
            self.germany_order, army_silesia, self.silesia, self.berlin,
            self.prussia
        )
        fleet_baltic_support = support(
            self.germany_order, fleet_baltic, self.baltic_sea, self.berlin,
            self.prussia
        )

        army_prussia_support = support(
            self.italy_order, army_prussia, self.prussia, self.livonia,
            self.prussia
        )

        army_warsaw_support = support(
            self.russia_order, army_warsaw, self.warsaw, self.livonia,
            self.prussia
        )
        army_livonia_move = move(
            self.russia_order, army_livonia, self.livonia, self.prussia,
        )
        commands = [
            army_berlin_move, army_silesia_support, fleet_baltic_support,
            army_prussia_support, army_warsaw_support, army_livonia_move,
            army_prussia
        ]
        models.Command.objects.process_commands()
        [c.refresh_from_db() for c in commands]

        self.assertTrue(army_prussia_support.illegal)
        self.assertEqual(
            army_prussia_support.illegal_message,
            ('Cannot support to territory that is not adjacent to the '
             'supporting piece.')
        )

        self.assertTrue(army_berlin_move.succeeds)
        self.assertTrue(army_prussia.dislodged)
        self.assertTrue(
            army_prussia.dislodged_by,
            army_berlin
        )
