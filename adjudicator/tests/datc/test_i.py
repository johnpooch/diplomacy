import unittest

from adjudicator import illegal_messages
from adjudicator.decisions import Outcomes
from adjudicator.order import Build
from adjudicator.piece import Army, Fleet, PieceTypes
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestRetreating(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_fleets_cannot_be_built_inland(self):
        """
        Physically this is possible, but it is still not allowed.

        Russia has one build and Moscow is empty.

        Russia:
        Build F Moscow
        See issue 4.C.4. Some game masters will change the order and build an
        army in Moscow.

        I prefer that the build fails.
        """
        orders = [
            Build(0, Nations.RUSSIA, self.territories.MOSCOW, PieceTypes.FLEET),
        ]
        self.state.register(*orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].illegal_message, illegal_messages.B005)

    def test_supply_center_must_be_empty_for_building(self):
        """
        You can't have two units in a sector. So, you can't build when there is a unit in the supply center.

        Germany may build a unit but has an army in Berlin. Germany orders the following:

        Germany:
        Build A Berlin

        Build fails.
        """
        pieces = [
            Army(0, Nations.GERMANY, self.territories.BERLIN),
        ]
        orders = [
            Build(0, Nations.GERMANY, self.territories.BERLIN, PieceTypes.ARMY),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].illegal_message, illegal_messages.B001)

    def test_both_coasts_must_be_empty_for_building(self):
        """
        If a sector is occupied on one coast, the other coast can not be used
        for building.

        Russia may build a unit and has a fleet in St Petersburg(sc). Russia
        orders the following:

        Russia:
        Build A St Petersburg(nc)

        Build fails.
        """
        pieces = [
            Fleet(0, Nations.RUSSIA, self.territories.ST_PETERSBURG, self.named_coasts.ST_PETERSBURG_NC),
        ]
        orders = [
            Build(0, Nations.RUSSIA, self.territories.ST_PETERSBURG, PieceTypes.FLEET, self.named_coasts.ST_PETERSBURG_SC),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].illegal_message, illegal_messages.B001)

    def test_building_in_home_supply_center_that_is_not_owned(self):
        """
        Building a unit is only allowed when supply center is a home supply
        center and is owned. If not owned, build fails.
        """
        self.territories.ST_PETERSBURG.controlled_by = Nations.GERMANY
        orders = [
            Build(0, Nations.RUSSIA, self.territories.ST_PETERSBURG, PieceTypes.FLEET, self.named_coasts.ST_PETERSBURG_SC),
        ]
        self.state.register(*orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].illegal_message, illegal_messages.B004)

    def test_building_in_owned_supply_center_that_is_not_home(self):
        """
        Building a unit is only allowed when supply center is a home supply
        center and is owned. If it is not a home supply center, the build fails.
        """
        self.territories.ST_PETERSBURG.controlled_by = Nations.GERMANY
        orders = [
            Build(0, Nations.GERMANY, self.territories.ST_PETERSBURG, PieceTypes.FLEET, self.named_coasts.ST_PETERSBURG_SC),
        ]
        self.state.register(*orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].illegal_message, illegal_messages.B003)
