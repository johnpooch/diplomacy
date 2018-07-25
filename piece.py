class Piece:
    def __init__(self, territory, owner):
        self.territory = territory
        self.owner = owner
        
    def must_retreat(self):
        self.retreat = True
        
    def retreat_resolved(self):
        self.retreat = False
        
class Army(Piece):
    def __init__(self, territory, owner):
        Piece.__init__(self, territory, owner)
        pass

class Fleet(Piece):
    def __init__(self, territory, owner):
        Piece.__init__(self, territory, owner)
        pass

piece_1 = Army("eng", "england")
piece_2 = Army("bre", "france")

    
    
