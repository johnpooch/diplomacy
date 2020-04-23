import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestConvoys(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

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
        pieces = [
            Army(0, Nations.TURKEY, self.territories.GREECE),
            Fleet(0, Nations.TURKEY, self.territories.AEGEAN_SEA),
            Fleet(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Fleet(0, Nations.TURKEY, self.territories.BLACK_SEA),
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.GREECE, self.territories.SEVASTAPOL, via_convoy=True),
            Convoy(0, Nations.TURKEY, self.territories.AEGEAN_SEA, self.territories.GREECE, self.territories.SEVASTAPOL),
            Convoy(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.GREECE, self.territories.SEVASTAPOL),
            Convoy(0, Nations.TURKEY, self.territories.BLACK_SEA, self.territories.GREECE, self.territories.SEVASTAPOL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[0].legal_decision, Outcomes.LEGAL)
        self.assertEqual(orders[2].legal_decision, Outcomes.ILLEGAL)

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

        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Army(0, Nations.FRANCE, self.territories.PARIS),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.LONDON, self.territories.BREST),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BREST, via_convoy=True),
            Move(0, Nations.FRANCE, self.territories.PARIS, self.territories.BREST),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.ENGLAND, self.territories.MID_ATLANTIC),
            Army(0, Nations.FRANCE, self.territories.PARIS),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.LONDON, self.territories.BREST),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BREST, via_convoy=True),
            Support(0, Nations.ENGLAND, self.territories.MID_ATLANTIC, self.territories.LONDON, self.territories.BREST),
            Move(0, Nations.FRANCE, self.territories.PARIS, self.territories.BREST),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.GERMANY, self.territories.SKAGERRAK)
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.HOLLAND),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.HOLLAND, via_convoy=True),
            Move(0, Nations.GERMANY, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
            Fleet(0, Nations.FRANCE, self.territories.BELGIUM),
            Fleet(0, Nations.GERMANY, self.territories.SKAGERRAK),
            Fleet(0, Nations.GERMANY, self.territories.DENMARK)
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.HOLLAND),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.HOLLAND, via_convoy=True),
            Move(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.NORTH_SEA),
            Support(0, Nations.FRANCE, self.territories.BELGIUM, self.territories.ENGLISH_CHANNEL, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
            Support(0, Nations.GERMANY, self.territories.DENMARK, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[5].support_decision, Outcomes.GIVEN)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Army(0, Nations.GERMANY, self.territories.HOLLAND),
            Army(0, Nations.GERMANY, self.territories.BELGIUM),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.GERMANY, self.territories.SKAGERRAK),
            Army(0, Nations.FRANCE, self.territories.PICARDY),
            Army(0, Nations.FRANCE, self.territories.BURGUNDY),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.HOLLAND),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.HOLLAND, via_convoy=True),
            Support(0, Nations.GERMANY, self.territories.HOLLAND, self.territories.BELGIUM, self.territories.BELGIUM),
            Support(0, Nations.GERMANY, self.territories.BELGIUM, self.territories.HOLLAND, self.territories.HOLLAND),
            Support(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
            Move(0, Nations.FRANCE, self.territories.PICARDY, self.territories.BELGIUM),
            Support(0, Nations.FRANCE, self.territories.BURGUNDY, self.territories.PICARDY, self.territories.BELGIUM),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[1].path_decision(), Outcomes.NO_PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].support_decision, Outcomes.CUT)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[4].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[5].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[6].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[7].support_decision, Outcomes.GIVEN)

    @unittest.skip('test_dislodged_convoy_does_not_cause_contested_area - involves retreat')
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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.GERMANY, self.territories.SKAGERRAK),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.HOLLAND),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.HOLLAND, via_convoy=True),
            Support(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[1].path_decision(), Outcomes.NO_PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.MOVES)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT),
            Fleet(0, Nations.GERMANY, self.territories.SKAGERRAK),
            Army(0, Nations.GERMANY, self.territories.BELGIUM),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.HOLLAND),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.HOLLAND, via_convoy=True),
            Support(0, Nations.GERMANY, self.territories.HELGOLAND_BIGHT, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.SKAGERRAK, self.territories.NORTH_SEA),
            Move(0, Nations.GERMANY, self.territories.BELGIUM, self.territories.HOLLAND),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[1].path_decision(), Outcomes.NO_PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[3].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[4].move_decision, Outcomes.MOVES)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL),
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.FRANCE, self.territories.BREST),
            Fleet(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.LONDON, self.territories.BELGIUM),
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Support(0, Nations.FRANCE, self.territories.BREST, self.territories.MID_ATLANTIC, self.territories.ENGLISH_CHANNEL),
            Move(0, Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.ENGLISH_CHANNEL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[1].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[2].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.MOVES)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.GERMANY, self.territories.ENGLISH_CHANNEL),
            Fleet(0, Nations.FRANCE, self.territories.BREST),
            Fleet(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Convoy(0, Nations.GERMANY, self.territories.ENGLISH_CHANNEL, self.territories.LONDON, self.territories.BELGIUM),
            Support(0, Nations.FRANCE, self.territories.BREST, self.territories.MID_ATLANTIC, self.territories.ENGLISH_CHANNEL),
            Move(0, Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.ENGLISH_CHANNEL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[1].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.MOVES)

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
        pieces = [
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.GERMANY, self.territories.ENGLISH_CHANNEL),
            Fleet(0, Nations.RUSSIA, self.territories.NORTH_SEA),
            Fleet(0, Nations.FRANCE, self.territories.BREST),
            Fleet(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
        ]
        orders = [
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Convoy(0, Nations.GERMANY, self.territories.ENGLISH_CHANNEL, self.territories.LONDON, self.territories.BELGIUM),
            Convoy(0, Nations.RUSSIA, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Support(0, Nations.FRANCE, self.territories.BREST, self.territories.MID_ATLANTIC, self.territories.ENGLISH_CHANNEL),
            Move(0, Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.ENGLISH_CHANNEL),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(pieces[1].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.MOVES)

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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.ENGLAND, self.territories.IRISH_SEA),
            Fleet(0, Nations.FRANCE, self.territories.NORTH_ATLANTIC),
            Fleet(0, Nations.FRANCE, self.territories.MID_ATLANTIC),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.LONDON, self.territories.BELGIUM),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Convoy(0, Nations.ENGLAND, self.territories.IRISH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Support(0, Nations.FRANCE, self.territories.NORTH_ATLANTIC, self.territories.MID_ATLANTIC, self.territories.IRISH_SEA),
            Move(0, Nations.FRANCE, self.territories.MID_ATLANTIC, self.territories.IRISH_SEA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(pieces[0].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[1].path_decision(), Outcomes.PATH)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(pieces[2].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[4].move_decision, Outcomes.MOVES)

    @unittest.skip('test_simple_convoy_paradox - Convoy paradox')
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
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.ENGLAND, self.territories.WALES),
            Army(0, Nations.FRANCE, self.territories.BREST),
            Fleet(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
        ]
        orders = [
            Support(0, Nations.ENGLAND, self.territories.LONDON, self.territories.WALES, self.territories.ENGLISH_CHANNEL),
            Move(0, Nations.ENGLAND, self.territories.WALES, self.territories.ENGLISH_CHANNEL),
            Move(0, Nations.FRANCE, self.territories.BREST, self.territories.LONDON),
            Convoy(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.BREST, self.territories.LONDON),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].support_decision, Outcomes.GIVEN)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].path_decision, Outcomes.NO_PATH)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.DISLODGED)

    # @unittest.skip
    # def test_simple_convoy_paradox_with_additional_convoy(self):
    #     """
    #     Paradox rules only apply on the paradox core.
    #     England:
    #     F London Supports F Wales - English Channel
    #     F Wales - English Channel
    #     France:
    #     A Brest - London
    #     F English Channel Convoys A Brest - London
    #     Italy:
    #     F Irish Sea Convoys A North Africa - Wales
    #     F Mid-Atlantic Ocean Convoys A North Africa - Wales
    #     A North Africa - Wales
    #     The Italian convoy is not part of the paradox core and should therefore
    #     succeed when the move of the fleet in Wales is successful. This is the
    #     case except when the 'All Hold' paradox rule is used (fully applied,
    #     not just as "backup" rule, see issue 4.A.2).
    #     I prefer the Szykman rule, so I prefer that both the fleet in Wales as
    #     the army in North Africa succeed in moving.
    #     """
    #     fleet_london = cap(
    #         self.turn, self.england, fleet, self.london, support, self.wales,
    #         self.english_channel
    #     )
    #     fleet_wales = cap(
    #         self.turn, self.england, fleet, self.wales, move,
    #         target=self.english_channel
    #     )
    #     army_brest = cap(
    #         self.turn, self.france, army, self.brest, move, target=self.london,
    #     )
    #     fleet_english_channel = cap(
    #         self.turn, self.france, fleet, self.english_channel, convoy,
    #         self.brest, self.london
    #     )
    #     fleet_irish_sea = cap(
    #         self.turn, self.italy, fleet, self.irish_sea, convoy,
    #         self.north_africa, self.wales
    #     )
    #     fleet_mid_atlantic = cap(
    #         self.turn, self.italy, fleet, self.mid_atlantic, convoy,
    #         self.north_africa, self.wales
    #     )
    #     army_north_africa = cap(
    #         self.turn, self.italy, army, self.north_africa, move,
    #         target=self.wales,
    #     )
    #
    #     models.Command.objects.process()
    #     [v.refresh_from_db() for v in locals().values() if v != self]
    #
    #     self.assertTrue(fleet_london.command.succeeds)
    #     self.assertTrue(fleet_wales.command.succeeds)
    #     self.assertTrue(army_brest.command.fails)
    #     self.assertTrue(fleet_english_channel.command.fails)
    #     self.assertEqual(
    #         fleet_english_channel.dislodged_by,
    #         fleet_wales
    #     )
    #     self.assertTrue(army_north_africa.command.succeeds)
    #     self.assertTrue(fleet_irish_sea.command.succeeds)
    #     self.assertTrue(fleet_mid_atlantic.command.succeeds)
    #
    # @unittest.skip
    # def test_pandins_paradox(self):
    #     """
    #     In Pandin's paradox, the attacked unit protects the convoying fleet by
    #     a beleaguered garrison.
    #     England:
    #     F London Supports F Wales - English Channel
    #     F Wales - English Channel
    #     France:
    #     A Brest - London
    #     F English Channel Convoys A Brest - London
    #     Germany:
    #     F North Sea Supports F Belgium - English Channel
    #     F Belgium - English Channel
    #     In all the different rules for resolving convoy disruption paradoxes
    #     (see issue 4.A.2), the support of London is not cut. That means that
    #     the fleet in the English Channel is not dislodged and none of the units
    #     succeed to move.
    #     """
    #     fleet_london = cap(
    #         self.turn, self.england, fleet, self.london, support, self.wales,
    #         self.english_channel
    #     )
    #     fleet_wales = cap(
    #         self.turn, self.england, fleet, self.wales, move,
    #         target=self.english_channel
    #     )
    #     army_brest = cap(
    #         self.turn, self.france, army, self.brest, move, target=self.london,
    #     )
    #     fleet_english_channel = cap(
    #         self.turn, self.france, fleet, self.english_channel, convoy,
    #         self.brest, self.london
    #     )
    #     fleet_north_sea = cap(
    #         self.turn, self.germany, fleet, self.north_sea, support,
    #         self.belgium, self.english_channel
    #     )
    #     fleet_belgium = cap(
    #         self.turn, self.germany, fleet, self.belgium, move,
    #         target=self.english_channel
    #     )

    # NOTE there are more of these!
    #