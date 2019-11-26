class Piece:
    all_pieces = []

    def __init__(self, nation, territory):
        self.__class__.all_pieces.append(self)
        self.nation = nation
        self.territory = territory


class Army(Piece):
    pass


class Fleet(Piece):
    def __init__(self, nation, territory, named_coast=None):
        super().__init__(nation, territory)  # DRY - do not repeat yourself
        self.named_coast = named_coast
