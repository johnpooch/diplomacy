# Player ==========================================================================================

class Player():
    all_players = []
    def __init__(self, username, email, password, nation):
        Player.all_nations.append(self)
        self.username = username
        self.email = email
        self.password = password
        self.nation = nation
        self.orders_finalised = False
        
# =================================================================================================