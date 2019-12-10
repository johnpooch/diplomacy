UNRESOLVED = 'unresolved'
PATH = 'path'
NO_PATH = 'no path'

SUCCEEDS = 'succeeds'
FAILS = 'fails'


class ConvoyChain:
    '''
    Represents a chain of one or more fleet paths which are attempting to convoy an army from a source to a destination.
   '''

    def __init__(self, fleets):
        self.fleets = fleets
        self.result = UNRESOLVED


class Path:
    '''
For each piece ordered to move, the decision whether there is a path from the source to the destination. This decision will result in `path` or `no_path`. When the move is without any convoy, the decision always results in 'path'.
    '''

    def __init__(self, piece, target, convoy_chains=[]):
        self.piece = piece
        self.source = piece.territory
        self.target = target
        self.result = UNRESOLVED
        self.convoy_chains = convoy_chains

    def __call__(self):
        '''
Return the result of the decision if resolved. Otherwise attempt resolve the decision and then return the result
        '''
        if self.result != UNRESOLVED:
            return self.result

        self.result = self._resolve()
        return self.result

    def _resolve(self):

        if not self.piece.order.via_convoy:
            return PATH

        if not self.convoy_chains:
            return NO_PATH
        if any([c.result == SUCCEEDS for c in self.convoy_chains]):
            return PATH

        if all([c.result == FAILS for c in self.convoy_chains]):
            return NO_PATH

        return UNRESOLVED
