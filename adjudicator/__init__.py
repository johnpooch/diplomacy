from adjudicator.processor import process
from adjudicator.serializers import GameSerializer
from adjudicator.state import State


def process_game_state(data):

    # Instantiate `State` for this turn
    state = State()

    # Deserialize data into game state - deserializing registers instance with
    # the state.
    game_serializer = GameSerializer(
        context={'state': state},
        data=data,
    )

    # Ensure that provided data is valid
    if not game_serializer.is_valid():
        raise ValueError('Game state data is invalid')
    game_serializer.save()

    # Process game state
    process(state)

    # Serialize processed game state and return
    game_serializer = GameSerializer(state)
    return game_serializer.data
