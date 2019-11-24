class Order:
    def __init__(self, nation, source):
        self.nation = nation
        self.source = source


class Hold(Order):
    pass


class Move(Order):
    def __init__(self, nation, source, target, via_convoy=False):
        super().__init__(nation, source)
        self.target = target
        self.via_convoy = via_convoy


class Support(Order):
    def __init__(self, nation, source, aux, target):
        super().__init__(nation, source)
        self.aux = aux
        self.target = target


class Convoy(Order):
    def __init__(self, nation, source, aux, target):
        super().__init__(nation, source)
        self.aux = aux
        self.target = target
