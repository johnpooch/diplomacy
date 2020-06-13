import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Convoy, Hold, Move, Support
from adjudicator.piece import Army, Fleet
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import Nations, Territories, register_all


class TestTurn(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.state = register_all(self.state, self.territories, [])

    def test_turn(self):
        pass
