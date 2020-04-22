from copy import deepcopy
from adjudicator.decisions import Outcomes


class ConvoyChain:
    """
    Represents a chain of one or more fleet paths which are attempting to
    convoy an army from a source to a destination.
    """

    def __init__(self, convoys):
        self.convoys = list(convoys)
        self.result = Outcomes.UNRESOLVED

    def resolve(self):

        if all([c.piece.dislodged_decision == Outcomes.SUSTAINS for c in self.convoys]) and \
                all([c.legal_decision == Outcomes.LEGAL for c in self.convoys]):
            self.result = Outcomes.SUCCEEDS
            return

        if any([c.piece.dislodged_decision == Outcomes.DISLODGED for c in self.convoys]) or \
                any([c.legal_decision == Outcomes.ILLEGAL for c in self.convoys]):
            self.result = Outcomes.FAILS
            return
        self.result = Outcomes.UNRESOLVED


def get_convoy_chains(source, target, convoys):
    """
    Given a list of convoy orders, get every convoy chain between `source` and
    `target`. It is assumed that the convoys are convoying from `source` to
    `target`.

    Args:
        * `source` - `Territory`
        * `target` - `Territory`
        * `convoys` - `list` of `Convoy` instances

    returns:
        * `list` where each element in the list is a `ConvoyChain` instance.
    """
    convoy_paths = set()
    for convoy in convoys:
        if convoy.source.adjacent_to(source):
            # if direct convoy
            if convoy.source.adjacent_to(target):
                # add single order tuple to `convoy_paths`
                path = (convoy,)
                convoy_paths.add(path)
            else:
                remaining = [c for c in convoys if not c == convoy]
                paths = build_chain([convoy], target, remaining)
                if paths:
                    [convoy_paths.add(p) for p in paths]
    return [ConvoyChain(p) for p in list(convoy_paths)]


def build_chain(initial_chain, target, convoys):
    """
    Recursive method which attempts to build a chain of convoying orders
    to a given ``target``.
    """
    complete_chains = []
    for convoy in convoys:
        # if order neigbouring last node in chain, add order to chain
        if convoy.source.adjacent_to(initial_chain[-1].source):
            chain = initial_chain + [convoy]

            # path found - neighbouring piece is adjacent to target
            if convoy.source.adjacent_to(target):
                complete_chains.append(tuple(chain))
                continue

            # path not found - check new node's neighbours (recurse)
            remaining = [c for c in convoys if not c == convoy]
            inner_chains = build_chain(chain, target, remaining)

            # if the inner method returns complete chains, add them to
            # outer method's complete chains
            if inner_chains:
                complete_chains.append(inner_chains[0])

    if complete_chains:
        return complete_chains
