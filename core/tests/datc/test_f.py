import unittest

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


class TestConvoys(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'supply_centers.json']

    # NOTE these should be moved to a class setup method.
    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.initialise_named_coasts()
        self.initialise_nations()
        self.initialise_orders()

    def test_no_convoy_in_coastal_area(self):
        """
        A fleet in a coastal area may not convoy.

        Turkey:
        A Greece - Sevastopol
        F Aegean Sea Convoys A Greece - Sevastopol
        F Constantinople Convoys A Greece - Sevastopol
        F Black Sea Convoys A Greece - Sevastopol

        The convoy in Constantinople is not possible. So, the army in Greece
        will not move to Sevastopol.
        """
        army_greece = cap(  # noqa: F841
            self.turkey, army, self.greece, move, target=self.sevastapol
        )
        fleet_aegean = cap(
            self.turkey, fleet, self.aegean_sea, convoy, self.greece,
            self.sevastapol
        )
        fleet_constantinople = cap(
            self.turkey, fleet, self.constantinople, convoy, self.greece,
            self.sevastapol
        )
        fleet_black_sea = cap(
            self.turkey, fleet, self.black_sea, convoy, self.greece,
            self.sevastapol
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertFalse(army_greece.command.illegal)
        self.assertTrue(army_greece.command.fails)

        self.assertFalse(fleet_aegean.command.illegal)
        self.assertFalse(fleet_black_sea.command.illegal)

        self.assertEqual(
            fleet_constantinople.command.illegal_message,
            'Cannot convoy unless piece is at sea.'
        )

    def test_army_being_convoyed_can_bounce_as_normal(self):
        """
        Armies being convoyed bounce on other units just as armies that are not
        being convoyed.

        England:
        F English Channel Convoys A London - Brest
        A London - Brest

        France:
        A Paris - Brest

        The English army in London bounces on the French army in Paris. Both
        units do not move.
        """
        fleet_english_channel = cap(
            self.england, fleet, self.english_channel, convoy, self.london,
            self.brest
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.brest
        )
        army_paris = cap(
            self.france, army, self.paris, move, target=self.brest
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_english_channel.command.succeeds)

        self.assertTrue(army_london.command.fails)
        self.assertTrue(army_paris.command.fails)

    def test_army_being_convoyed_can_receive_support(self):
        """
        Armies being convoyed can receive support as in any other move.

        England:
        F English Channel Convoys A London - Brest
        A London - Brest
        F Mid-Atlantic Ocean Supports A London - Brest

        France:
        A Paris - Brest

        The army in London receives support and beats the army in Paris. This
        means that the army London will end in Brest and the French army in
        Paris stays in Paris.
        """
        fleet_english_channel = cap(
            self.england, fleet, self.english_channel, convoy, self.london,
            self.brest
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.brest
        )
        fleet_mid_atlantic = cap(
            self.england, fleet, self.mid_atlantic, support, self.london, self.brest
        )
        army_paris = cap(
            self.france, army, self.paris, move, target=self.brest
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_english_channel.command.succeeds)
        self.assertTrue(fleet_mid_atlantic.command.succeeds)
        self.assertTrue(army_london.command.succeeds)
        self.assertTrue(army_paris.command.fails)

    def test_attacked_convoy_is_not_disrupted(self):
        """
        A convoy can only be disrupted by dislodging the fleets. Attacking is
        not sufficient.

        England:
        F North Sea Convoys A London - Holland
        A London - Holland

        Germany:
        F Skagerrak - North Sea

        The army in London will successfully convoy and end in Holland.
        """
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, convoy, self.london,
            self.holland
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.holland
        )
        fleet_skagerrak = cap(
            self.germany, fleet, self.skagerrak, move, target=self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.command.succeeds)
        self.assertTrue(army_london.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.fails)

    def test_beleaguered_convoy_is_not_disrupted(self):
        """
        Even when a convoy is in a beleaguered garrison it is not disrupted.

        England:
        F North Sea Convoys A London - Holland
        A London - Holland

        France:
        F English Channel - North Sea
        F Belgium Supports F English Channel - North Sea

        Germany:
        F Skagerrak - North Sea
        F Denmark Supports F Skagerrak - North Sea

        The army in London will successfully convoy and end in Holland.
        """
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, convoy, self.london,
            self.holland
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.holland
        )
        fleet_english_channel = cap(
            self.france, fleet, self.english_channel, move,
            target=self.north_sea
        )
        fleet_belgium = cap(
            self.france, fleet, self.belgium, support, self.english_channel,
            self.north_sea
        )
        fleet_skagerrak = cap(
            self.germany, fleet, self.skagerrak, move, target=self.north_sea
        )
        fleet_denmark = cap(
            self.germany, fleet, self.denmark, support, self.skagerrak,
            self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.command.succeeds)
        self.assertTrue(army_london.command.succeeds)

        self.assertTrue(fleet_english_channel.command.fails)
        self.assertTrue(fleet_belgium.command.succeeds)

        self.assertTrue(fleet_skagerrak.command.fails)
        self.assertTrue(fleet_denmark.command.succeeds)

    def test_dislodged_convoy_does_not_cut_support(self):
        """
        When a fleet of a convoy is dislodged, the convoy is completely
        cancelled. So, no support is cut.

        England:
        F North Sea Convoys A London - Holland
        A London - Holland

        Germany:
        A Holland Supports A Belgium
        A Belgium Supports A Holland
        F Helgoland Bight Supports F Skagerrak - North Sea
        F Skagerrak - North Sea

        France:
        A Picardy - Belgium
        A Burgundy Supports A Picardy - Belgium

        The hold order of Holland on Belgium will sustain and Belgium will not
        be dislodged by the French in Picardy.
        """
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, convoy, self.london,
            self.holland
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.holland
        )
        army_holland = cap(
            self.germany, army, self.holland, support, self.belgium,
            self.belgium
        )
        army_belgium = cap(
            self.germany, army, self.belgium, support, self.holland,
            self.holland
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, support, self.skagerrak,
            self.north_sea
        )
        fleet_skagerrak = cap(
            self.germany, fleet, self.skagerrak, move, target=self.north_sea
        )
        army_picardy = cap(
            self.france, army, self.picardy, move, target=self.belgium
        )
        army_burgundy = cap(
            self.france, army, self.burgundy, support, self.picardy,
            self.belgium
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(army_holland.sustains)
        self.assertTrue(army_belgium.sustains)

        self.assertTrue(fleet_north_sea.command.fails)
        self.assertTrue(army_london.command.fails)

        self.assertTrue(fleet_helgoland_bight.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)

        self.assertTrue(army_picardy.command.fails)
        self.assertTrue(army_burgundy.command.succeeds)

    def test_dislodged_convoy_does_not_cause_contested_area(self):
        """
        When a fleet of a convoy is dislodged, the landing area is not
        contested, so other units can retreat to that area.

        England:
        F North Sea Convoys A London - Holland
        A London - Holland

        Germany:
        F Helgoland Bight Supports F Skagerrak - North Sea
        F Skagerrak - North Sea

        The dislodged English fleet can retreat to Holland.
        """
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, convoy, self.london,
            self.holland
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.holland
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, support, self.skagerrak,
            self.north_sea
        )
        fleet_skagerrak = cap(
            self.germany, fleet, self.skagerrak, move, target=self.north_sea
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.command.fails)
        self.assertTrue(army_london.command.fails)

        self.assertTrue(fleet_helgoland_bight.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)
        print('finish when retreat is done')

    def test_dislodged_convoy_does_not_cause_a_bounce(self):
        """
        When a fleet of a convoy is dislodged, then there will be no bounce in
        the landing area.

        England:
        F North Sea Convoys A London - Holland
        A London - Holland

        Germany:
        F Helgoland Bight Supports F Skagerrak - North Sea
        F Skagerrak - North Sea
        A Belgium - Holland

        The army in Belgium will not bounce and move to Holland.
        """
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, convoy, self.london,
            self.holland
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.holland
        )
        fleet_helgoland_bight = cap(
            self.germany, fleet, self.helgoland_bight, support, self.skagerrak,
            self.north_sea
        )
        fleet_skagerrak = cap(
            self.germany, fleet, self.skagerrak, move, target=self.north_sea
        )
        army_belgium = cap(
            self.germany, army, self.belgium, move, target=self.holland
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_north_sea.command.fails)
        self.assertTrue(army_london.command.fails)

        self.assertTrue(fleet_helgoland_bight.command.succeeds)
        self.assertTrue(fleet_skagerrak.command.succeeds)

        self.assertTrue(army_belgium.command.succeeds)

    def test_dislodged_multi_route_convoy(self):
        """
        When a fleet of a convoy with multiple routes is dislodged, the result
        depends on the rulebook that is used.

        England:
        F English Channel Convoys A London - Belgium
        F North Sea Convoys A London - Belgium
        A London - Belgium

        France:
        F Brest Supports F Mid-Atlantic Ocean - English Channel
        F Mid-Atlantic Ocean - English Channel

        The French fleet in Mid Atlantic Ocean will dislodge the convoying
        fleet in the English Channel. If the 1971 rules are used (see issue
        4.A.1), this will disrupt the convoy and the army will stay in London.
        When the 1982 or 2000 rulebook is used (which I prefer) the army can
        still go via the North Sea and the convoy succeeds and the London army
        will end in Belgium.
        """
        fleet_english_channel = cap(
            self.england, fleet, self.english_channel, convoy, self.london,
            self.belgium
        )
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, convoy, self.london,
            self.belgium
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.belgium
        )
        fleet_brest = cap(
            self.france, fleet, self.brest, support, self.mid_atlantic,
            self.english_channel
        )
        fleet_mid_atlantic = cap(
            self.france, fleet, self.mid_atlantic, move,
            target=self.english_channel,
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertEqual(
            fleet_english_channel.dislodged_by,
            fleet_mid_atlantic
        )
        self.assertTrue(fleet_english_channel.command.fails)
        self.assertTrue(fleet_north_sea.command.succeeds)
        self.assertTrue(army_london.command.succeeds)
        self.assertTrue(fleet_brest.command.succeeds)
        self.assertTrue(fleet_mid_atlantic.command.succeeds)

    def test_dislodge_of_multi_route_convoy_with_foreign_fleet(self):
        """
        When the 1971 rulebook is used "unwanted" multi-route convoys are
        possible.

        England:
        F North Sea Convoys A London - Belgium
        A London - Belgium

        Germany:
        F English Channel Convoys A London - Belgium

        France:
        F Brest Supports F Mid-Atlantic Ocean - English Channel
        F Mid-Atlantic Ocean - English Channel

        If the 1982 or 2000 rulebook is used (which I prefer), it makes no
        difference that the convoying fleet in the English Channel is German.
        It will take the convoy via the North Sea anyway and the army in London
        will end in Belgium.  However, when the 1971 rules are used, the German
        convoy is "unwanted".  According to the DPTG the German fleet should be
        ignored in the English convoy, since there is a convoy path with only
        English fleets. That means that the convoy is not disrupted and the
        English army in London will end in Belgium. See also issue 4.A.1.
        """
        fleet_north_sea = cap(
            self.england, fleet, self.north_sea, convoy, self.london,
            self.belgium
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.belgium
        )
        fleet_english_channel = cap(
            self.germany, fleet, self.english_channel, convoy, self.london,
            self.belgium
        )
        fleet_brest = cap(
            self.france, fleet, self.brest, support, self.mid_atlantic,
            self.english_channel
        )
        fleet_mid_atlantic = cap(
            self.france, fleet, self.mid_atlantic, move,
            target=self.english_channel,
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertEqual(
            fleet_english_channel.dislodged_by,
            fleet_mid_atlantic
        )
        self.assertTrue(fleet_english_channel.command.fails)
        self.assertTrue(fleet_north_sea.command.succeeds)
        self.assertTrue(army_london.command.succeeds)
        self.assertTrue(fleet_brest.command.succeeds)
        self.assertTrue(fleet_mid_atlantic.command.succeeds)

    def test_dislodge_of_multi_route_convoy_with_only_foreign_fleets(self):
        """
        When the 1971 rulebook is used, "unwanted" convoys can not be ignored
        in all cases.

        England:
        A London - Belgium

        Germany:
        F English Channel Convoys A London - Belgium

        Russia:
        F North Sea Convoys A London - Belgium

        France:
        F Brest Supports F Mid-Atlantic Ocean - English Channel
        F Mid-Atlantic Ocean - English Channel

        If the 1982 or 2000 rulebook is used (which I prefer), it makes no
        difference that the convoying fleets are not English. It will take the
        convoy via the North Sea anyway and the army in London will end in
        Belgium.

        However, when the 1971 rules are used, the situation is different.
        Since both the fleet in the English Channel as the fleet in North Sea
        are not English, it can not be concluded that the German fleet is
        "unwanted". Therefore, one of the routes of the convoy is disrupted and
        that means that the complete convoy is disrupted. The army in London
        will stay in London. See also issue 4.A.1.
        """
        army_london = cap(
            self.england, army, self.london, move, target=self.belgium
        )
        fleet_english_channel = cap(
            self.germany, fleet, self.english_channel, convoy, self.london,
            self.belgium
        )
        fleet_north_sea = cap(
            self.russia, fleet, self.north_sea, convoy, self.london,
            self.belgium
        )
        fleet_brest = cap(
            self.france, fleet, self.brest, support, self.mid_atlantic,
            self.english_channel
        )
        fleet_mid_atlantic = cap(
            self.france, fleet, self.mid_atlantic, move,
            target=self.english_channel,
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertEqual(
            fleet_english_channel.dislodged_by,
            fleet_mid_atlantic
        )
        self.assertTrue(fleet_english_channel.command.fails)
        self.assertTrue(fleet_north_sea.command.succeeds)
        self.assertTrue(army_london.command.succeeds)
        self.assertTrue(fleet_brest.command.succeeds)
        self.assertTrue(fleet_mid_atlantic.command.succeeds)

    def test_dislodge_convoying_fleet_not_on_route(self):
        """
        When the rule is used that convoys are disrupted when one of the routes
        is disrupted (see issue 4.A.1), the convoy is not necessarily disrupted
        when one of the fleets ordered to convoy is dislodged.

        England:
        F English Channel Convoys A London - Belgium
        A London - Belgium
        F Irish Sea Convoys A London - Belgium

        France:
        F North Atlantic Ocean Supports F Mid-Atlantic Ocean - Irish Sea
        F Mid-Atlantic Ocean - Irish Sea

        Even when convoys are disrupted when one of the routes is disrupted
        (see issue 4.A.1), the convoy from London to Belgium will still
        succeed, since the dislodged fleet in the Irish Sea is not part of any
        route, although it can be reached from the starting point London.
        """
        fleet_english_channel = cap(
            self.england, fleet, self.english_channel, convoy, self.london,
            self.belgium
        )
        army_london = cap(
            self.england, army, self.london, move, target=self.belgium
        )
        fleet_irish_sea = cap(
            self.england, fleet, self.irish_sea, convoy, self.london,
            self.belgium
        )
        fleet_north_atlantic = cap(
            self.france, fleet, self.north_atlantic, support,
            self.mid_atlantic, self.irish_sea
        )
        fleet_mid_atlantic = cap(
            self.france, fleet, self.mid_atlantic, move,
            target=self.irish_sea,
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertEqual(
            fleet_irish_sea.dislodged_by,
            fleet_mid_atlantic
        )
        self.assertTrue(fleet_english_channel.command.succeeds)
        self.assertTrue(army_london.command.succeeds)
        self.assertTrue(fleet_irish_sea.command.fails)
        self.assertEqual(
            fleet_irish_sea.dislodged_by,
            fleet_mid_atlantic
        )
        self.assertTrue(fleet_mid_atlantic.command.succeeds)
        self.assertTrue(fleet_north_atlantic.command.succeeds)

    @unittest.skip
    def test_simple_convoy_paradox(self):
        """
        The most common paradox is when the attacked unit supports an attack on
        one of the convoying fleets.

        England:
        F London Supports F Wales - English Channel
        F Wales - English Channel

        France:
        A Brest - London
        F English Channel Convoys A Brest - London

        This situation depends on how paradoxes are handled (see issue (4.A.2).
        In case of the 'All Hold' rule (fully applied, not just as "backup"
        rule), both the movement of the English fleet in Wales as the France
        convoy in Brest are part of the paradox and fail. In all other rules of
        paradoxical convoys (including the Szykman rule which I prefer), the
        support of London is not cut. That means that the fleet in the English
        Channel is dislodged.
        """
        fleet_london = cap(
            self.england, fleet, self.london, support, self.wales,
            self.english_channel
        )
        fleet_wales = cap(
            self.england, fleet, self.wales, move, target=self.english_channel
        )
        army_brest = cap(
            self.france, army, self.brest, move, target=self.london,
        )
        fleet_english_channel = cap(
            self.france, fleet, self.english_channel, convoy,
            self.brest, self.london
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_london.command.succeeds)
        self.assertTrue(fleet_wales.command.succeeds)
        self.assertTrue(army_brest.command.fails)
        self.assertTrue(fleet_english_channel.command.fails)
        self.assertEqual(
            fleet_english_channel.dislodged_by,
            fleet_wales
        )

    @unittest.skip
    def test_simple_convoy_paradox_with_additional_convoy(self):
        """
        Paradox rules only apply on the paradox core.

        England:
        F London Supports F Wales - English Channel
        F Wales - English Channel

        France:
        A Brest - London
        F English Channel Convoys A Brest - London

        Italy:
        F Irish Sea Convoys A North Africa - Wales
        F Mid-Atlantic Ocean Convoys A North Africa - Wales
        A North Africa - Wales

        The Italian convoy is not part of the paradox core and should therefore
        succeed when the move of the fleet in Wales is successful. This is the
        case except when the 'All Hold' paradox rule is used (fully applied,
        not just as "backup" rule, see issue 4.A.2).

        I prefer the Szykman rule, so I prefer that both the fleet in Wales as
        the army in North Africa succeed in moving.
        """
        fleet_london = cap(
            self.england, fleet, self.london, support, self.wales,
            self.english_channel
        )
        fleet_wales = cap(
            self.england, fleet, self.wales, move, target=self.english_channel
        )
        army_brest = cap(
            self.france, army, self.brest, move, target=self.london,
        )
        fleet_english_channel = cap(
            self.france, fleet, self.english_channel, convoy,
            self.brest, self.london
        )
        fleet_irish_sea = cap(
            self.italy, fleet, self.irish_sea, convoy, self.north_africa,
            self.wales
        )
        fleet_mid_atlantic = cap(
            self.italy, fleet, self.mid_atlantic, convoy, self.north_africa,
            self.wales
        )
        army_north_africa = cap(
            self.italy, army, self.north_africa, move, target=self.wales,
        )

        models.Command.objects.process_commands()
        [v.refresh_from_db() for v in locals().values() if v != self]

        self.assertTrue(fleet_london.command.succeeds)
        self.assertTrue(fleet_wales.command.succeeds)
        self.assertTrue(army_brest.command.fails)
        self.assertTrue(fleet_english_channel.command.fails)
        self.assertEqual(
            fleet_english_channel.dislodged_by,
            fleet_wales
        )
        self.assertTrue(army_north_africa.command.succeeds)
        self.assertTrue(fleet_irish_sea.command.succeeds)
        self.assertTrue(fleet_mid_atlantic.command.succeeds)

    @unittest.skip
    def test_pandins_paradox(self):
        """
        In Pandin's paradox, the attacked unit protects the convoying fleet by
        a beleaguered garrison.

        England:
        F London Supports F Wales - English Channel
        F Wales - English Channel

        France:
        A Brest - London
        F English Channel Convoys A Brest - London

        Germany:
        F North Sea Supports F Belgium - English Channel
        F Belgium - English Channel

        In all the different rules for resolving convoy disruption paradoxes
        (see issue 4.A.2), the support of London is not cut. That means that
        the fleet in the English Channel is not dislodged and none of the units
        succeed to move.
        """
        fleet_london = cap(
            self.england, fleet, self.london, support, self.wales,
            self.english_channel
        )
        fleet_wales = cap(
            self.england, fleet, self.wales, move, target=self.english_channel
        )
        army_brest = cap(
            self.france, army, self.brest, move, target=self.london,
        )
        fleet_english_channel = cap(
            self.france, fleet, self.english_channel, convoy,
            self.brest, self.london
        )
        fleet_north_sea = cap(
            self.germany, fleet, self.north_sea, support, self.belgium,
            self.english_channel
        )
        fleet_belgium = cap(
            self.germany, fleet, self.belgium, move,
            target=self.english_channel
        )
