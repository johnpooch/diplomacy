from adjudicator import order, piece, territory
from adjudicator.named_coast import NamedCoast
from adjudicator.nation import Nation
from adjudicator.base import OrderType, Phase, PieceType, Season, TerritoryType
from adjudicator.processor import process
from adjudicator.schema import TurnSchema
from adjudicator.state import State


territory_type_dict = {
    TerritoryType.SEA: territory.SeaTerritory,
    TerritoryType.INLAND: territory.InlandTerritory,
    TerritoryType.COASTAL: territory.CoastalTerritory,
}

order_type_dict = {
    OrderType.HOLD: order.Hold,
    OrderType.MOVE: order.Move,
    OrderType.SUPPORT: order.Support,
    OrderType.CONVOY: order.Convoy,
    OrderType.RETREAT: order.Retreat,
    OrderType.DISBAND: order.Disband,
    OrderType.BUILD: order.Build,
}

piece_type_dict = {
    PieceType.ARMY: piece.Army,
    PieceType.FLEET: piece.Fleet,
}


def process_game_state(data):
    territory_map = {}
    named_coast_map = {}

    # Marshall data into expected format and validate
    validated_data = TurnSchema().load(data)

    season = validated_data['season']
    phase = validated_data['phase']
    year = validated_data['year']

    # Instantiate `State` for this turn
    state = State(season, phase, year)

    # Initialise territory instances and register each to state. Add to
    # territory map
    for territory_data in validated_data['territories']:
        territory_type = territory_data.pop('type')
        territory_class = territory_type_dict[territory_type]
        territory = territory_class(state, **territory_data)
        territory_map[territory_data['id']] = territory

    # Initialise named coasts - grab parent from territory map
    for named_coast_data in validated_data['named_coasts']:
        named_coast_data['parent'] = territory_map[named_coast_data['parent']]
        named_coast = NamedCoast(state, **named_coast_data)
        named_coast_map[named_coast.id] = named_coast

    # Initialise orders - grab source, target, aux, target_coast from maps
    for order_data in validated_data['orders']:
        order_type = order_data.pop('type')
        order_class = order_type_dict[order_type]
        for arg_name in ['source', 'target', 'aux']:
            territory_id = order_data[arg_name]
            if territory_id:
                order_data[arg_name] = territory_map[territory_id]
        target_coast_id = order_data['target_coast']
        if target_coast_id:
            order_data['target_coast'] = named_coast_map[target_coast_id]
        order_class(state, **order_data)

    # Initialise pieces - grab source, target, aux, target_coast from maps
    for piece_data in validated_data['pieces']:
        piece_type = piece_data.pop('type')
        piece_class = piece_type_dict[piece_type]
        for arg_name in ['territory', 'attacker_territory']:
            territory_id = piece_data[arg_name]
            if territory_id:
                piece_data[arg_name] = territory_map[territory_id]
        named_coast_id = piece_data['named_coast']
        if named_coast_id:
            piece_data['named_coast'] = named_coast_map[named_coast_id]
        piece_class(state, **piece_data)

    # Initialise nation instances and register each to state
    for nation_data in validated_data['nations']:
        Nation(state, **nation_data)

    # Process game state
    process(state)

    # Serialize processed game state and return
    processed_data = TurnSchema().dump(state)
    return processed_data


def get_next_season_phase_and_year(state, season, phase, year):
    if any(p for p in state.pieces if p.dislodged and not p.destroyed):
        return season, Phase.RETREAT, year

    if season == Season.SPRING:
        return Season.FALL, Phase.ORDER, year

    if season == Season.FALL and not phase == Phase.BUILD:
        # TODO work out if change in possession has happened
        return season, Phase.BUILD, year

    return Season.SPRING, Phase.ORDER, year + 1
