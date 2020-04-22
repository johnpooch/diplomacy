class Outcomes:
    UNRESOLVED = 'unresolved'
    PATH = 'path'
    NO_PATH = 'no path'
    SUCCEEDS = 'succeeds'
    FAILS = 'fails'
    MOVES = 'moves'
    GIVEN = 'given'
    CUT = 'cut'
    LEGAL = 'legal'
    ILLEGAL = 'illegal'
    DISLODGED = 'dislodged'
    SUSTAINS = 'sustains'


class Decision:

    def __init__(self, order):
        self.order = order
        self.result = Outcomes.UNRESOLVED

    def __call__(self):
        """
        Return the result of the decision if resolved. Otherwise attempt
        resolve the decision and then return the result
        """
        if self.result != Outcomes.UNRESOLVED:
            return self.result
        self.result = self._resolve()
        return self.result

    def _resolve(self):
        raise NotImplementedError(
            'Subclasses of Decision must implement _resolve method.'
        )
