"""
This script contains the Piece class and its subclasses, 'Army' and 'Fleet'.
"""


class Piece:
    def __init__(self, territory, nation):
        self.territory = territory
        self.nation = nation
        
        
class Army(Piece):
    def __init__(self, territory, nation):
        Piece.__init__(self, territory, nation)


class Fleet(Piece):
    def __init__(self, territory, nation, identified_coast=None):
        Piece.__init__(self, territory, nation)
        self.identified_coast = identified_coast

