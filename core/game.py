"""
Functions relating to processing and updating the game. Interacts with
the `adjudicator` module.
"""
from adjudicator import process_game_state

from core import models
from core.models.base import DrawStatus, OrderType, OutcomeType, Phase, Season
from core.serializers import TurnSerializer


def process_turn(turn):
    """
    Serialize the given turn into the format the `adjudicator` expects. Pass
    the turn the adjudicator. Update the turn based on the adjudicator
    response.
    """
    turn_data = TurnSerializer(turn).data
    outcome = process_game_state(turn_data)
    updated_turn = update_turn(turn, outcome)

    new_turn = create_turn_from_previous_turn(updated_turn)
    # check win conditions
    winning_nation = new_turn.check_for_winning_nation()
    if winning_nation:
        turn.game.set_winner(winning_nation)
    return new_turn


def update_turn(turn, data):
    """
    Deserialize the `adjudicator` response and update the turn based on the
    response data.
    """
    # Deserialize data - updates piece states, territory states, and orders
    serializer = TurnSerializer(instance=turn, data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()

    # Additional updates to the turn that aren't handled during deserialization
    destroy_pieces(turn)
    if turn.phase in [Phase.RETREAT_AND_DISBAND, Phase.BUILD]:
        disband_pieces(turn)
    if turn.phase == Phase.BUILD:
        create_new_pieces(turn)
    return instance


def expire_draws(turn):
    """
    Expire unresolved draw proposals at the end of a turn
    """
    draws = []
    for draw in turn.draws.all():
        if draw.status == DrawStatus.PROPOSED:
            draw.status = DrawStatus.EXPIRED
            draw.save()
            draws.append(draw)
    return draws


def destroy_pieces(turn):
    """
    Set `turn_destroyed` for every piece which is destroyed
    """
    pieces = []
    destroyed_piece_states = turn.piecestates.filter(destroyed=True)
    for piece_state in destroyed_piece_states:
        piece = piece_state.piece
        piece.turn_destroyed = turn
        piece.save()
        pieces.append(piece)
    return pieces


def disband_pieces(turn):
    """
    Set `turn_disbanded` for every piece with a successful disband order.
    """
    # TODO handle no disband order given
    pieces = []
    successful_disbands = turn.orders.filter(
        type=OrderType.DISBAND,
        outcome=OutcomeType.SUCCEEDS
    )
    # set `turn_disbanded` for all disbanded pieces
    for order in successful_disbands:
        piece = order.source.pieces.get(
            turn=turn,
            piece__nation=order.nation,
        ).piece
        piece.turn_disbanded = turn
        piece.save()
        pieces.append(piece)
    return pieces


def create_new_pieces(turn):
    """
    Create a new `Piece` and `PieceState` instance for each successful build
    order.
    """
    new_pieces = []
    successful_builds = turn.orders.filter(
        type=OrderType.BUILD,
        outcome=OutcomeType.SUCCEEDS,
    )
    for order in successful_builds:
        piece = order.nation.pieces.create(
            game=turn.game,
            turn_created=turn,
            type=order.piece_type,
        )
        turn.piecestates.create(
            piece=piece,
            territory=order.source,
            named_coast=order.target_coast,
        )
        new_pieces.append(piece)
    return new_pieces


def create_turn_from_previous_turn(turn):

    # We need to create the turn new turn to create related objects but we
    # don't know what year, season, and phase the turn will be until later.
    new_turn = models.Turn.objects.new(
        game=turn.game,
        year=0,
        season=Season.SPRING,
        phase=Phase.ORDER,
        current_turn=True,
    )

    # Copy over objects from previous turn
    for piece_state in turn.piecestates.all():
        piece_state.copy_to_new_turn(new_turn)
    for territory_state in turn.territorystates.all():
        territory_state.copy_to_new_turn(new_turn)
    for nation_state in turn.nationstates.all():
        nation_state.copy_to_new_turn(new_turn)

    # Determine next turn season, phase, and year
    new_turn.season, new_turn.phase, new_turn.year = \
        get_next_season_phase_and_year(turn, new_turn)
    new_turn.save()

    return new_turn


def get_next_season_phase_and_year(old_turn, new_turn):
    if not old_turn.processed:
        raise ValueError('Cannot get next phase until order is processed.')

    if old_turn.piecestates.filter(dislodged=True).exists():
        return old_turn.season, Phase.RETREAT_AND_DISBAND, old_turn.year

    if old_turn.season == Season.SPRING:
        return Season.FALL, Phase.ORDER, old_turn.year

    if old_turn.season == Season.FALL and not old_turn.phase == Phase.BUILD:
        for nation_state in new_turn.nationstates.all():
            if abs(nation_state.supply_delta):
                return old_turn.season, Phase.BUILD, old_turn.year
    return Season.SPRING, Phase.ORDER, old_turn.year + 1
