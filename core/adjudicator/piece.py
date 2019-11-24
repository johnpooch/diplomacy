class Piece:
    def __init__(self, nation, territory):
        self.nation = nation
        self.territory = territory


class Army(Piece):
    pass


class Fleet(Piece):
    def __init__(self, nation, territory, named_coast=None):
        super().__init__(nation, territory)  # DRY - do not repeat yourself
        self.named_coast = named_coast
