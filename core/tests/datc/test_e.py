from core import models
from core.models.base import PieceType, CommandType
from core.tests.base import HelperMixin, TerritoriesMixin
from core.tests.base import command_and_piece as cap
from core.tests.base import InitialGameStateTestCase as TestCase

fleet = PieceType.FLEET
army = PieceType.ARMY

hold = CommandType.HOLD
move = CommandType.MOVE
support = CommandType.SUPPORT
convoy = CommandType.CONVOY


class TestHeadToHeadBattles(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'supply_centers.json']

    # NOTE these should be moved to a class setup method.
    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.initialise_named_coasts()
        self.initialise_nations()
        self.initialise_orders()

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
        army_berlin = cap(  # noqa: F841
            self.germany, army, self.berlin, move, target=self.prussia
        )
        fleet_kiel = cap(
            self.germany, fleet, self.kiel, move, target=self.berlin
        )
        army_silesia = cap(  # noqa: F841
            self.germany, army, self.silesia, support, self.berlin,
            self.prussia
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_kiel.command.succeeds)

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
        army_berlin = cap(
            self.germany, army, self.berlin, move, target=self.kiel
        )
        fleet_kiel = cap(
            self.germany, fleet, self.kiel, move, target=self.berlin
        )
        army_munich = cap(
            self.germany, army, self.munich, support, self.berlin,
            self.kiel
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_kiel.command.fails)
        self.assertTrue(army_berlin.command.fails)
        self.assertTrue(army_munich.command.succeeds)

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
        army_berlin = cap(
            self.germany, army, self.berlin, move, target=self.kiel
        )
        army_munich = cap(
            self.germany, army, self.munich, support, self.kiel,
            self.berlin
        )
        fleet_kiel = cap(
            self.england, fleet, self.kiel, move, target=self.berlin,
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(army_berlin.command.fails)
        self.assertTrue(army_munich.command.succeeds)
        self.assertTrue(fleet_kiel.command.fails)

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
        fleet_holland = cap(
            self.germany, fleet, self.holland, move, target=self.north_sea,
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, support,
            self.holland, self.north_sea
        )
        fleet_skagerrak = cap(
            self.germany, fleet, self.skagerrak, support, self.holland,
            self.north_sea
        )
        fleet_north_sea = cap(
            self.france, fleet, self.north_sea, move, target=self.holland,
        )
        fleet_belgium = cap(
            self.france, fleet, self.belgium, support, self.north_sea,
            self.holland
        )
        fleet_edinburgh = cap(
            self.england, fleet, self.edinburgh, support,
            self.norwegian_sea, self.north_sea
        )
        fleet_yorkshire = cap(
            self.england, fleet, self.yorkshire, support,
            self.norwegian_sea, self.north_sea
        )
        fleet_norwegian_sea = cap(
            self.england, fleet, self.norwegian_sea, move,
            target=self.north_sea
        )
        army_kiel = cap(
            self.austria, army, self.kiel, support, self.ruhr, self.holland
        )
        army_ruhr = cap(
            self.austria, army, self.ruhr, move, target=self.holland
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_holland.command.fails)
        self.assertTrue(fleet_norwegian_sea.command.fails)
        self.assertTrue(fleet_north_sea.command.fails)
        self.assertTrue(army_ruhr.command.fails)

        self.assertTrue(fleet_helgoland_bight.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)
        self.assertTrue(fleet_belgium.command.succeeds)
        self.assertTrue(fleet_edinburgh.command.succeeds)
        self.assertTrue(fleet_yorkshire.command.succeeds)
        self.assertTrue(army_kiel.command.succeeds)

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
        fleet_holland = cap(
            self.germany, fleet, self.holland, move, target=self.north_sea,
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, support,
            self.holland, self.north_sea
        )
        fleet_skagerrak = cap(
            self.germany, fleet, self.skagerrak, support, self.holland,
            self.north_sea
        )
        fleet_north_sea = cap(
            self.france, fleet, self.north_sea, move, target=self.holland,
        )
        fleet_belgium = cap(
            self.france, fleet, self.belgium, support, self.north_sea,
            self.holland
        )
        fleet_edinburgh = cap(
            self.england, fleet, self.edinburgh, support,
            self.norwegian_sea, self.north_sea
        )
        fleet_yorkshire = cap(
            self.england, fleet, self.yorkshire, support,
            self.norwegian_sea, self.north_sea
        )
        fleet_norwegian_sea = cap(
            self.england, fleet, self.norwegian_sea, move,
            target=self.north_sea
        )
        fleet_london = cap(
            self.england, fleet, self.london, support,
            self.norwegian_sea, self.north_sea
        )
        army_kiel = cap(
            self.austria, army, self.kiel, support, self.ruhr, self.holland
        )
        army_ruhr = cap(
            self.austria, army, self.ruhr, move, target=self.holland
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertEqual(fleet_north_sea.dislodged_by, fleet_norwegian_sea)
        self.assertTrue(army_ruhr.command.fails)
        self.assertTrue(fleet_holland.command.fails)
        self.assertTrue(fleet_holland.sustains)

        self.assertTrue(fleet_helgoland_bight.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)
        self.assertTrue(fleet_belgium.command.succeeds)
        self.assertTrue(fleet_edinburgh.command.succeeds)
        self.assertTrue(fleet_yorkshire.command.succeeds)
        self.assertTrue(fleet_london.command.succeeds)
        self.assertTrue(army_kiel.command.succeeds)

    def test_no_self_dislodgement_with_beleauguered_garrison(self):
        """
        An attempt to self dislodge can be combined with a beleaguered
        garrison. Such self dislodgment is still not possible.

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
        # NOTE this is very tricky to implement. Right now I'm not implementing
        # any specific functionality for this. It just seems to work out.
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, hold
        )
        fleet_yorkshire = cap(
            self.england, fleet, self.yorkshire, support, self.norway,
            self.north_sea
        )
        fleet_holland = cap(
            self.germany, fleet, self.holland, support,
            self.helgoland_bight, self.north_sea
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, move,
            target=self.north_sea
        )
        fleet_skagerrak = cap(
            self.russia, fleet, self.skagerrak, support,
            self.norway, self.north_sea
        )
        fleet_norway = cap(
            self.russia, fleet, self.norway, move, target=self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.sustains)
        self.assertTrue(fleet_helgoland_bight.command.fails)
        self.assertTrue(fleet_norway.command.fails)

        # self.assertTrue(fleet_yorkshire.command.fails)
        self.assertTrue(fleet_holland.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)

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
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, move, target=self.norway
        )
        fleet_yorkshire = cap(
            self.england, fleet, self.yorkshire, support, self.norway,
            self.north_sea
        )
        fleet_holland = cap(
            self.germany, fleet, self.holland, support,
            self.helgoland_bight, self.north_sea
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, move,
            target=self.north_sea
        )
        fleet_skagerrak = cap(
            self.russia, fleet, self.skagerrak, support,
            self.norway, self.north_sea
        )
        fleet_norway = cap(
            self.russia, fleet, self.norway, move, target=self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.sustains)
        self.assertTrue(fleet_north_sea.command.fails)
        self.assertTrue(fleet_helgoland_bight.command.fails)
        self.assertTrue(fleet_norway.command.fails)

        self.assertTrue(fleet_yorkshire.command.succeeds)
        self.assertTrue(fleet_holland.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)

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
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, move,
            target=self.norwegian_sea
        )
        fleet_yorkshire = cap(
            self.england, fleet, self.yorkshire, support, self.norway,
            self.north_sea
        )
        fleet_holland = cap(
            self.germany, fleet, self.holland, support,
            self.helgoland_bight, self.north_sea
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, move,
            target=self.north_sea
        )
        fleet_skagerrak = cap(
            self.russia, fleet, self.skagerrak, support,
            self.norway, self.north_sea
        )
        fleet_norway = cap(
            self.russia, fleet, self.norway, move, target=self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.command.succeeds)
        self.assertTrue(fleet_helgoland_bight.command.fails)
        self.assertTrue(fleet_yorkshire.command.succeeds)
        self.assertTrue(fleet_norway.command.succeeds)

        self.assertTrue(fleet_holland.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)

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
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, move, target=self.denmark
        )
        fleet_yorkshire = cap(
            self.england, fleet, self.yorkshire, support, self.norway,
            self.north_sea
        )
        fleet_holland = cap(
            self.germany, fleet, self.holland, support,
            self.helgoland_bight, self.north_sea
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, move,
            target=self.north_sea
        )
        fleet_denmark = cap(
            self.germany, fleet, self.denmark, move,
            target=self.helgoland_bight
        )
        fleet_skagerrak = cap(
            self.russia, fleet, self.skagerrak, support,
            self.norway, self.north_sea
        )
        fleet_norway = cap(
            self.russia, fleet, self.norway, move, target=self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.command.fails)
        self.assertTrue(fleet_helgoland_bight.command.fails)
        self.assertTrue(fleet_norway.command.fails)
        self.assertTrue(fleet_denmark.command.fails)

        self.assertTrue(fleet_yorkshire.command.succeeds)
        self.assertTrue(fleet_holland.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)

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
        army_spain = cap(
            self.france, army, self.spain, move, target=self.portugal,
            via_convoy=True,
        )
        fleet_mid_atlantic = cap(
            self.france, fleet, self.mid_atlantic, convoy, self.spain,
            self.portugal
        )
        fleet_gulf_of_lyon = cap(
            self.france, fleet, self.gulf_of_lyon, support,
            self.portugal, self.spain, self.spain_sc
        )
        army_marseilles = cap(
            self.germany, army, self.marseilles, support,
            self.gascony, self.spain
        )
        army_gascony = cap(
            self.germany, army, self.gascony, move,
            target=self.spain
        )
        fleet_portugal = cap(
            self.italy, fleet, self.portugal, move,
            target=self.spain, target_coast=self.spain_nc
        )
        fleet_western_med = cap(
            self.italy, fleet, self.western_mediterranean, support,
            self.portugal, self.spain
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(army_spain.command.succeeds)
        self.assertTrue(fleet_mid_atlantic.command.succeeds)
        self.assertTrue(fleet_gulf_of_lyon.command.succeeds)

        self.assertTrue(army_marseilles.command.succeeds)
        self.assertTrue(army_gascony.command.fails)

        self.assertTrue(fleet_portugal.command.succeeds)
        self.assertTrue(fleet_western_med.command.succeeds)

    def support_on_attack_on_own_unit_can_be_used_for_other_means(self):
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
        army_budapest = cap(
            self.austria, army, self.budapest, move, target=self.rumania
        )
        army_serbia = cap(
            self.austria, army, self.serbia, support, self.vienna,
            self.budapest
        )
        army_vienna = cap(
            self.italy, army, self.vienna, move, target=self.budapest,
        )
        army_galicia = cap(
            self.russia, army, self.galicia, move, target=self.budapest,
        )
        army_rumania = cap(
            self.russia, army, self.rumania, support, self.galicia,
            self.budapest
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(army_serbia.command.succeeds)
        self.assertTrue(army_budapest.command.fails)
        self.assertTrue(army_vienna.command.fails)
        self.assertTrue(army_galicia.command.fails)
        self.assertTrue(army_rumania.command.succeeds)

    def three_way_beleaguered_garrison(self):
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
        fleet_edinburgh = cap(
            self.england, fleet, self.edinburgh, support, self.yorkshire,
            self.north_sea
        )
        fleet_yorkshire = cap(
            self.england, fleet, self.yorkshire, move, target=self.north_sea,
        )
        fleet_belgium = cap(
            self.france, fleet, self.belgium, move, target=self.north_sea
        )
        fleet_english_channel = cap(
            self.france, fleet, self.english_channel, support, self.belgium,
            self.north_sea
        )
        fleet_north_sea = cap(
            self.germany, fleet, self.north_sea, hold
        )
        fleet_norwegian_sea = cap(
            self.russia, fleet, self.norwegian_sea, move, target=self.north_sea
        )
        fleet_norway = cap(
            self.russia, fleet, self.norway, support, self.norwegian_sea,
            self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.sustains)

        self.assertTrue(fleet_yorkshire.command.fails)
        self.assertTrue(fleet_belgium.command.fails)
        self.assertTrue(fleet_norwegian_sea.command.fails)

        self.assertTrue(fleet_edinburgh.command.succeeds)
        self.assertTrue(fleet_english_channel.command.succeeds)
        self.assertTrue(fleet_norway.command.succeeds)

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
        army_liverpool = cap(
            self.england, army, self.liverpool, move, target=self.edinburgh
        )
        fleet_edinburgh = cap(
            self.russia, fleet, self.edinburgh, move, target=self.liverpool
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_edinburgh.command.illegal)
        self.assertTrue(army_liverpool.command.fails)

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
        fleet_holland = cap(
            self.england, fleet, self.holland, support, self.ruhr, self.kiel
        )
        army_ruhr = cap(
            self.england, army, self.ruhr, move, target=self.kiel
        )
        army_kiel = cap(
            self.france, army, self.kiel, move, target=self.berlin
        )
        army_munich = cap(  # noqa: F841
            self.france, army, self.munich, support, self.kiel, self.berlin
        )
        army_silesia = cap(  # noqa: F841
            self.france, army, self.silesia, support, self.kiel, self.berlin
        )
        army_berlin = cap(
            self.germany, army, self.berlin, move, target=self.kiel
        )
        fleet_denmark = cap(  # noqa: F841
            self.germany, fleet, self.denmark, support, self.berlin, self.kiel
        )
        fleet_helgoland_bight = cap(  # noqa: F841
            self.germany, fleet, self.helgoland_bight, support, self.berlin,
            self.kiel
        )
        fleet_baltic = cap(  # noqa
            self.russia, fleet, self.baltic_sea, support, self.prussia,
            self.berlin
        )
        army_prussia = cap(
            self.russia, army, self.prussia, move, target=self.berlin
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(army_ruhr.command.fails)
        self.assertTrue(army_kiel.command.fails)
        self.assertTrue(army_berlin.command.fails)
        self.assertTrue(army_prussia.command.fails)

        self.assertTrue(fleet_holland.command.succeeds)
