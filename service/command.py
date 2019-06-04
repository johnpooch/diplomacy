
"""
This script contains the Command class
"""


class Command:
    def __init__(self, nation):
        self.nation = nation
        self.result = "success"
        self.log = None


class Hold(Command):
    def __init__(self, nation, source):
        Command.__init__(self, nation)
        self.source = source


class Move(Command):
    def __init__(self, nation, source, target):
        Command.__init__(self, nation)
        self.source = source
        self.target = target


class Support(Command):
    def __init__(self, nation, source, aux, target):
        Command.__init__(self, nation)
        self.source = source
        self.aux = aux
        self.target = target


class Convoy(Command):
    def __init__(self, nation, source, aux, target):
        Command.__init__(self, nation)
        self.source = source
        self.aux = aux
        self.target = target

