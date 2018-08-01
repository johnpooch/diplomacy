from write_to_log import write_to_log

# Nation ==========================================================================================

class Nation():
    all_nations = []
    def __init__(self, name, pieces, num_supply_centres):
        Nation.all_nations.append(self)
        self.name = name
        self.pieces = pieces
        self.num_supply_centres = num_supply_centres
        self.orders_submitted = False
        self.surrendered = False
        self.available = True
        self.player = None
        
    # Assign nation -------------------------------------------------------------------------

    def assign_player(self, username):
        if self.available:
            setattr(self, "available", False)
            setattr(self, "player", username)
        
class Neutral():
    def __init__(self):
        self.name = "neutral"
        
# =================================================================================================