import random
from game_state import game_state

available_nations = ["austria", "england", "france", "germany", "italy", "russia", "turkey"]
    
def create_player(username):
    nation = random.choice(available_nations)
    available_nations.remove(nation)
    # game_state["players"][username] = nation

def get_game_state():
    return(game_state)