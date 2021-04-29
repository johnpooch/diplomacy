from adjudicator.base import Season, Phase
from adjudicator.decisions import Outcomes
from adjudicator.paradoxes import find_circular_movements


def process(state):
    """
    Processes all orders in a turn.
    """
    orders = state.orders
    pieces = state.pieces
    for order in orders:
        order.check_legal()

    moves = [o for o in orders if o.is_move]
    retreats = [o for o in orders if o.is_retreat]
    supports = [o for o in orders if o.is_support]
    convoys = [o for o in orders if o.is_convoy]
    builds = [o for o in orders if o.is_build]

    illegal_retreats = [r for r in retreats if r.illegal]
    # set illegal retreats to fail.
    for r in illegal_retreats:
        r.outcome = Outcomes.FAILS

    illegal_moves = [m for m in moves if m.illegal]
    # set illegal moves to fail.
    for m in illegal_moves:
        m.outcome = Outcomes.FAILS

    unresolved_pieces = [p for p in pieces if p.dislodged_decision == Outcomes.UNRESOLVED]
    unresolved_supports = [s for s in supports if s.outcome == Outcomes.UNRESOLVED]

    unresolved_convoys = [c for c in convoys if c.piece.dislodged_decision == Outcomes.UNRESOLVED]
    while unresolved_convoys:
        unresolved_supports = [s for s in supports if s.outcome == Outcomes.UNRESOLVED]
        unresolved_moves = [m for m in moves if m.outcome == Outcomes.UNRESOLVED]
        for move in unresolved_moves:
            move.resolve()
        for support in unresolved_supports:
            support.resolve()
        for piece in unresolved_pieces:
            piece.update_dislodged_decision()
        for convoy in unresolved_convoys:
            convoy.resolve()
        # resolve fleet movements
        unresolved_convoys = [c for c in convoys if c.outcome == Outcomes.UNRESOLVED]

    # refresh after convoys resolved
    unresolved_moves = [m for m in moves if m.outcome == Outcomes.UNRESOLVED]

    depth = 0
    unresolved_retreats = [r for r in retreats if r.outcome == Outcomes.UNRESOLVED]
    while unresolved_moves or unresolved_pieces or unresolved_supports or unresolved_retreats:
        unresolved_retreats = [r for r in retreats if r.outcome == Outcomes.UNRESOLVED]
        for r in unresolved_retreats:
            r.resolve()

        if depth == 10:
            circular_movements = find_circular_movements(moves)
            for li in circular_movements:
                for move in li:
                    move.outcome = Outcomes.SUCCEEDS

        for move in [m for m in moves if m.outcome == Outcomes.UNRESOLVED]:
            move.resolve()

        unresolved_supports = [s for s in supports if s.outcome == Outcomes.UNRESOLVED]
        for support in unresolved_supports:
            support.resolve()

        for piece in unresolved_pieces:
            piece.update_dislodged_decision()

        unresolved_moves = [m for m in moves if m.outcome == Outcomes.UNRESOLVED]
        unresolved_pieces = [p for p in pieces if p.dislodged_decision == Outcomes.UNRESOLVED]
        depth += 1

    # Check update bounce_occurred_during_turn on all territories
    for territory in state.territories:
        attacks = [o for o in orders if o.is_move and o.target == territory]
        bounce_occurred = False
        for attack in attacks:
            if attack.legal and attack.outcome == Outcomes.FAILS and \
                    attack.path_decision() == Outcomes.PATH:
                bounce_occurred = True
        territory.bounce_occurred = bounce_occurred

    # Check all dislodged pieces for pieces which can't retreat
    dislodged_pieces = [p for p in state.pieces
                        if p.dislodged_decision == Outcomes.DISLODGED]
    for piece in dislodged_pieces:
        if not piece.can_retreat():
            piece.destroyed = True
            piece.destroyed_message = (
                'Destroyed because piece cannot retreat to any neighboring '
                'territories.'
            )
    for build in builds:
        if build.legal:
            build.outcome = Outcomes.SUCCEEDS
        else:
            build.outcome = Outcomes.FAILS

    if state.phase == Phase.RETREAT:
        for piece in state.pieces:
            if piece.retreating and (piece.order.outcome == Outcomes.FAILS):
                piece.destroyed = True
                piece.destroyed_message = (
                    'Destroyed because piece must retreat but retreat order failed.'
                )

    # TODO test
    # TODO split into sub function
    # Set captured_by for territories if fall orders
    if state.season == Season.FALL and state.phase == Phase.ORDER:
        # Find all pieces that are not dislodged
        non_dislodged_pieces = [p for p in state.pieces if not p.dislodged]
        for piece in non_dislodged_pieces:
            # Ignore pieces that move successfully
            if piece.order.is_move and piece.order.outcome == Outcomes.SUCCEEDS:
                continue
            if piece.nation != getattr(piece.territory, 'controlled_by', False):
                if not (piece.territory.is_sea):
                    piece.territory.captured_by = piece.nation
        # Find all successful move orders
        successful_move_orders = [
            m for m in state.orders
            if m.is_move and m.outcome == Outcomes.SUCCEEDS
        ]
        for move in successful_move_orders:
            if move.piece.nation != getattr(move.target, 'controlled_by', False):
                if not (move.target.is_sea):
                    move.target.captured_by = move.piece.nation

    # Determine the next season, phase and year.
    state.next_season, state.next_phase, state.next_year = \
        get_next_season_phase_and_year(state)
    return state


def get_next_season_phase_and_year(state):
    if any(p for p in state.pieces if p.dislodged and not p.destroyed):
        return state.season, Phase.RETREAT, state.year

    if state.season == Season.SPRING:
        return Season.FALL, Phase.ORDER, state.year

    if state.season == Season.FALL and not state.phase == Phase.BUILD:
        for nation in state.nations:
            # TODO check for civil disorder nation
            if nation.next_turn_supply_delta != 0:
                return state.season, Phase.BUILD, state.year
    return Season.SPRING, Phase.ORDER, state.year + 1
