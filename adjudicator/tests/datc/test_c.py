import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Move, Support
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

    def test_three_army_circular_movement(self):
        """
        Three units can change place, even in spring 1901.

        Turkey:
        F Ankara - Constantinople
        A Constantinople - Smyrna
        A Smyrna - Ankara

        All three units will move.
        """
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Army(0, Nations.TURKEY, self.territories.SMYRNA)
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)

    def test_three_army_circular_movement_with_support(self):
        """
        Three units can change place, even when one gets support.

        Turkey:
        F Ankara - Constantinople
        A Constantinople - Smyrna
        A Smyrna - Ankara
        A Bulgaria Supports F Ankara - Constantinople

        Of course the three units will move, but knowing how programs are
        written, this can confuse the adjudicator.
        """
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Army(0, Nations.TURKEY, self.territories.SMYRNA)
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
            Support(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].support_decision, Outcomes.GIVEN)

    def test_disrupted_three_army_circular_movement(self):
        """
        When one of the units bounces, the whole circular movement will hold.

        Turkey:
        F Ankara - Constantinople
        A Constantinople - Smyrna
        A Smyrna - Ankara
        A Bulgaria - Constantinople

        Every unit will keep its place.
        """
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Army(0, Nations.TURKEY, self.territories.SMYRNA)
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
            Move(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.CONSTANTINOPLE),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)

    def test_circular_movement_with_attacked_convoy(self):
        """
        When the circular movement contains an attacked convoy, the circular
        movement succeeds. The adjudication algorithm should handle attack of
        convoys before calculating circular movement.

        Austria:
        A Trieste - Serbia
        A Serbia - Bulgaria

        Turkey:
        A Bulgaria - Trieste
        F Aegean Sea Convoys A Bulgaria - Trieste
        F Ionian Sea Convoys A Bulgaria - Trieste
        F Adriatic Sea Convoys A Bulgaria - Trieste

        Italy:
        F Naples - Ionian Sea

        The fleet in the Ionian Sea is attacked but not dislodged. The circular
        movement succeeds. The Austrian and Turkish armies will advance.
        """
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.AUSTRIA, self.territories.SERBIA),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
            Fleet(0, Nations.TURKEY, self.territories.AEGEAN_SEA),
            Fleet(0, Nations.TURKEY, self.territories.IONIAN_SEA),
            Fleet(0, Nations.TURKEY, self.territories.ADRIATIC_SEA),
            Fleet(0, Nations.ITALY, self.territories.NAPLES),
        ]
        orders = [
            Move(0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.SERBIA),
            Move(0, Nations.AUSTRIA, self.territories.SERBIA, self.territories.BULGARIA),
            Move(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.TRIESTE, via_convoy=True),
            Convoy(0, Nations.TURKEY, self.territories.AEGEAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(0, Nations.TURKEY, self.territories.IONIAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(0, Nations.TURKEY, self.territories.ADRIATIC_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Move(0, Nations.ITALY, self.territories.NAPLES, self.territories.IONIAN_SEA),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[2].move_decision, Outcomes.MOVES)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(pieces[4].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(pieces[5].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[6].move_decision, Outcomes.FAILS)

    def test_disrupted_circular_movement_due_to_dislodged_convoy(self):
        """
        When the circular movement contains a convoy, the circular movement is
        disrupted when the convoying fleet is dislodged. The adjudication
        algorithm should disrupt convoys before calculating circular movement.

        Austria:
        A Trieste - Serbia
        A Serbia - Bulgaria

        Turkey:
        A Bulgaria - Trieste
        F Aegean Sea Convoys A Bulgaria - Trieste
        F Ionian Sea Convoys A Bulgaria - Trieste
        F Adriatic Sea Convoys A Bulgaria - Trieste

        Italy:
        F Naples - Ionian Sea
        F Tunis Supports F Naples - Ionian Sea

        Due to the dislodged convoying fleet, all Austrian and Turkish armies
        will not move.
        """
        pieces = [
            Army(0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(0, Nations.AUSTRIA, self.territories.SERBIA),
            Army(0, Nations.TURKEY, self.territories.BULGARIA),
            Fleet(0, Nations.TURKEY, self.territories.AEGEAN_SEA),
            Fleet(0, Nations.TURKEY, self.territories.IONIAN_SEA),
            Fleet(0, Nations.TURKEY, self.territories.ADRIATIC_SEA),
            Fleet(0, Nations.ITALY, self.territories.NAPLES),
            Fleet(0, Nations.ITALY, self.territories.TUNIS),
        ]
        orders = [
            Move(0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.SERBIA),
            Move(0, Nations.AUSTRIA, self.territories.SERBIA, self.territories.BULGARIA),
            Move(0, Nations.TURKEY, self.territories.BULGARIA, self.territories.TRIESTE, via_convoy=True),
            Convoy(0, Nations.TURKEY, self.territories.AEGEAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(0, Nations.TURKEY, self.territories.IONIAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(0, Nations.TURKEY, self.territories.ADRIATIC_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Move(0, Nations.ITALY, self.territories.NAPLES, self.territories.IONIAN_SEA),
            Support(0, Nations.ITALY, self.territories.TUNIS, self.territories.NAPLES, self.territories.IONIAN_SEA),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(pieces[4].dislodged_decision, Outcomes.DISLODGED)
        self.assertEqual(pieces[4].dislodged_by, pieces[6])
        self.assertEqual(pieces[5].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[6].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[7].support_decision, Outcomes.GIVEN)

    def test_two_armies_with_two_convoys(self):
        """
        Two armies can swap places even when they are not adjacent.

        England:
        F North Sea Convoys A London - Belgium
        A London - Belgium

        France:
        F English Channel Convoys A Belgium - London
        A Belgium - London

        Both convoys should succeed.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
            Army(0, Nations.FRANCE, self.territories.BELGIUM),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Convoy(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.BELGIUM, self.territories.LONDON),
            Move(0, Nations.FRANCE, self.territories.BELGIUM, self.territories.LONDON, via_convoy=True),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].move_decision, Outcomes.MOVES)
        self.assertEqual(orders[3].move_decision, Outcomes.MOVES)

    def test_disrupted_unit_swap(self):
        """
        If in a swap one of the unit bounces, then the swap fails.

        England:
        F North Sea Convoys A London - Belgium
        A London - Belgium

        France:
        F English Channel Convoys A Belgium - London
        A Belgium - London
        A Burgundy - Belgium

        None of the units will succeed to move.
        """
        pieces = [
            Fleet(0, Nations.ENGLAND, self.territories.NORTH_SEA),
            Army(0, Nations.ENGLAND, self.territories.LONDON),
            Fleet(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
            Army(0, Nations.FRANCE, self.territories.BELGIUM),
            Army(0, Nations.FRANCE, self.territories.BURGUNDY),
        ]
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Move(0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Convoy(0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.BELGIUM, self.territories.LONDON),
            Move(0, Nations.FRANCE, self.territories.BELGIUM, self.territories.LONDON, via_convoy=True),
            Move(0, Nations.FRANCE, self.territories.BURGUNDY, self.territories.BELGIUM),
        ]

        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[3].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[4].move_decision, Outcomes.FAILS)
