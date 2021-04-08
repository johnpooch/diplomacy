from adjudicator.base import Phase, Season
from adjudicator.state import State


class AdjudicatorTestCaseMixin:

    def setUp(self):
        self.state = State(Season.SPRING, Phase.ORDER, 1900)
