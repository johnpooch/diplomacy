from adjudicator.decisions import Outcomes
from .state import register


class Nation:

    @register
    def __init__(self, state, id, name):
        self.id = id
        self.name = name
        self.state = state

    def __str__(self):
        return self.name

    @property
    def pieces(self):
        return [p for p in self.state.pieces if p.nation == self.id]

    @property
    def controlled_territories(self):
        return [t for t in self.state.territories if t.controlled_by == self.id]

    @property
    def captured_territories(self):
        return [t for t in self.state.territories if t.captured_by == self.id]

    @property
    def next_turn_piece_count(self):
        """
        Get the number of pieces that the nation will have going into the next
        turn.
        """
        return len([
            p for p in self.pieces if not p.destroyed and not
            (p.order.is_disband and p.order.outcome == Outcomes.SUCCEEDS)
        ])

    @property
    def next_turn_supply_center_count(self):
        """
        Get the number of supply centers that the nation will control going
        into the next turn.
        """
        territories = self.captured_territories
        for territory in self.controlled_territories:
            if not territory.captured_by:
                territories.append(territory)
        supply_centers = [t for t in territories if t.supply_center]
        return len(supply_centers)

    @property
    def next_turn_supply_delta(self):
        return self.next_turn_supply_center_count - self.next_turn_piece_count
