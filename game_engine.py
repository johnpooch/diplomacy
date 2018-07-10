import random
from opening_game_state import opening_game_state

available_nations = ["austria", "england", "france", "germany", "italy", "russia", "turkey"]

def create_player(username):
    nation = random.choice(available_nations)
    available_nations.remove(nation)
    opening_game_state["players"][username] = nation
    if not available_nations:
        game_state = initialise_game_state()
    return game_state

def initialise_game_state():
    game_state = opening_game_state
    print("game_state initialised")
    return game_state
