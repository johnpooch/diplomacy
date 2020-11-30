from adjudicator.state import State


class AdjudicatorTestCaseMixin:

    def setUp(self):
        self.state = State()
