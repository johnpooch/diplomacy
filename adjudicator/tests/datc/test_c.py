import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.tests.data import NamedCoasts, Nations, Territories

from ..base import AdjudicatorTestCaseMixin


class TestCircularMovement(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.territories = Territories(self.state)
        self.named_coasts = NamedCoasts(self.state, self.territories)

    def test_three_army_circular_movement(self):
        """
        Three units can change place, even in spring 1901.

        Turkey:
        F Ankara - Constantinople
        A Constantinople - Smyrna
        A Smyrna - Ankara

        All three units will move.
        """
        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        Army(self.state, 0, Nations.TURKEY, self.territories.SMYRNA)
        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
        ]
        process(self.state)

        self.assertEqual(orders[0].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[1].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[2].outcome, Outcomes.SUCCEEDS)

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
        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.BULGARIA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        Army(self.state, 0, Nations.TURKEY, self.territories.SMYRNA)
        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
            Support(self.state, 0, Nations.TURKEY, self.territories.BULGARIA, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
        ]
        process(self.state)

        self.assertEqual(orders[0].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[1].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[2].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[3].outcome, Outcomes.SUCCEEDS)

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
        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.BULGARIA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        Army(self.state, 0, Nations.TURKEY, self.territories.SMYRNA)
        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
            Move(self.state, 0, Nations.TURKEY, self.territories.BULGARIA, self.territories.CONSTANTINOPLE),
        ]

        process(self.state)

        self.assertEqual(orders[0].outcome, Outcomes.FAILS)
        self.assertEqual(orders[1].outcome, Outcomes.FAILS)
        self.assertEqual(orders[2].outcome, Outcomes.FAILS)
        self.assertEqual(orders[3].outcome, Outcomes.FAILS)

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
            Army(self.state, 0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(self.state, 0, Nations.AUSTRIA, self.territories.SERBIA),
            Army(self.state, 0, Nations.TURKEY, self.territories.BULGARIA),
            Fleet(self.state, 0, Nations.TURKEY, self.territories.AEGEAN_SEA),
            Fleet(self.state, 0, Nations.TURKEY, self.territories.IONIAN_SEA),
            Fleet(self.state, 0, Nations.TURKEY, self.territories.ADRIATIC_SEA),
            Fleet(self.state, 0, Nations.ITALY, self.territories.NAPLES),
        ]
        orders = [
            Move(self.state, 0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.SERBIA),
            Move(self.state, 0, Nations.AUSTRIA, self.territories.SERBIA, self.territories.BULGARIA),
            Move(self.state, 0, Nations.TURKEY, self.territories.BULGARIA, self.territories.TRIESTE, via_convoy=True),
            Convoy(self.state, 0, Nations.TURKEY, self.territories.AEGEAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(self.state, 0, Nations.TURKEY, self.territories.IONIAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(self.state, 0, Nations.TURKEY, self.territories.ADRIATIC_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Move(self.state, 0, Nations.ITALY, self.territories.NAPLES, self.territories.IONIAN_SEA),
        ]

        process(self.state)

        self.assertEqual(orders[0].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[1].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[2].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(pieces[3].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(pieces[4].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(pieces[5].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[6].outcome, Outcomes.FAILS)

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
            Army(self.state, 0, Nations.AUSTRIA, self.territories.TRIESTE),
            Army(self.state, 0, Nations.AUSTRIA, self.territories.SERBIA),
            Army(self.state, 0, Nations.TURKEY, self.territories.BULGARIA),
            Fleet(self.state, 0, Nations.TURKEY, self.territories.AEGEAN_SEA),
            Fleet(self.state, 0, Nations.TURKEY, self.territories.IONIAN_SEA),
            Fleet(self.state, 0, Nations.TURKEY, self.territories.ADRIATIC_SEA),
            Fleet(self.state, 0, Nations.ITALY, self.territories.NAPLES),
            Fleet(self.state, 0, Nations.ITALY, self.territories.TUNIS),
        ]
        orders = [
            Move(self.state, 0, Nations.AUSTRIA, self.territories.TRIESTE, self.territories.SERBIA),
            Move(self.state, 0, Nations.AUSTRIA, self.territories.SERBIA, self.territories.BULGARIA),
            Move(self.state, 0, Nations.TURKEY, self.territories.BULGARIA, self.territories.TRIESTE, via_convoy=True),
            Convoy(self.state, 0, Nations.TURKEY, self.territories.AEGEAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(self.state, 0, Nations.TURKEY, self.territories.IONIAN_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Convoy(self.state, 0, Nations.TURKEY, self.territories.ADRIATIC_SEA, self.territories.BULGARIA, self.territories.TRIESTE),
            Move(self.state, 0, Nations.ITALY, self.territories.NAPLES, self.territories.IONIAN_SEA),
            Support(self.state, 0, Nations.ITALY, self.territories.TUNIS, self.territories.NAPLES, self.territories.IONIAN_SEA),
        ]

        process(self.state)

        self.assertEqual(orders[0].outcome, Outcomes.FAILS)
        self.assertEqual(orders[1].outcome, Outcomes.FAILS)
        self.assertEqual(orders[2].outcome, Outcomes.FAILS)
        self.assertEqual(pieces[4].dislodged_by, pieces[6])
        self.assertEqual(pieces[5].dislodged_decision, Outcomes.SUSTAINS)
        self.assertEqual(orders[6].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[7].outcome, Outcomes.SUCCEEDS)

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
        Fleet(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA),
        Army(self.state, 0, Nations.ENGLAND, self.territories.LONDON),
        Fleet(self.state, 0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
        Army(self.state, 0, Nations.FRANCE, self.territories.BELGIUM),
        orders = [
            Convoy(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Move(self.state, 0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Convoy(self.state, 0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.BELGIUM, self.territories.LONDON),
            Move(self.state, 0, Nations.FRANCE, self.territories.BELGIUM, self.territories.LONDON, via_convoy=True),
        ]

        process(self.state)

        self.assertEqual(orders[1].outcome, Outcomes.SUCCEEDS)
        self.assertEqual(orders[3].outcome, Outcomes.SUCCEEDS)

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
        Fleet(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA),
        Army(self.state, 0, Nations.ENGLAND, self.territories.LONDON),
        Fleet(self.state, 0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL),
        Army(self.state, 0, Nations.FRANCE, self.territories.BELGIUM),
        Army(self.state, 0, Nations.FRANCE, self.territories.BURGUNDY),
        orders = [
            Convoy(self.state, 0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.LONDON, self.territories.BELGIUM),
            Move(self.state, 0, Nations.ENGLAND, self.territories.LONDON, self.territories.BELGIUM, via_convoy=True),
            Convoy(self.state, 0, Nations.FRANCE, self.territories.ENGLISH_CHANNEL, self.territories.BELGIUM, self.territories.LONDON),
            Move(self.state, 0, Nations.FRANCE, self.territories.BELGIUM, self.territories.LONDON, via_convoy=True),
            Move(self.state, 0, Nations.FRANCE, self.territories.BURGUNDY, self.territories.BELGIUM),
        ]

        process(self.state)

        self.assertEqual(orders[1].outcome, Outcomes.FAILS)
        self.assertEqual(orders[3].outcome, Outcomes.FAILS)
        self.assertEqual(orders[4].outcome, Outcomes.FAILS)
