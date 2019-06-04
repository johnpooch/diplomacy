from service.command import Hold, Move, Support, Convoy
from service.piece import Army, Fleet
from service.territory import InlandTerritory, CoastalTerritory, SeaTerritory


class CommandProcessor:
    """
    Determines the results of a list of commands.

    Returns a list of commands.
    """
    def __init__(self, territories, borders, identified_coast_borders, pieces, commands):
        self.territories = territories
        self.borders = borders
        self.identified_coast_borders = identified_coast_borders
        self.pieces = pieces
        self.commands = commands

    def process_commands(self):
        resolved_commands = []
        for command in self.commands:
            if not self._friendly_piece_exists_in_territory(command.nation, \
                    command.source):
                command.result = "invalid"
                resolved_commands.append(command)
                continue


            piece = self._get_friendly_piece_from_territory(command.nation, \
                    command.source)


            # TODO decompose into methods on the command

            if isinstance(command, (Move, Support, Convoy)):
                if not command.target.accessible_by_piece_type(piece):
                    command.result = "invalid"
                if not self._convoy_is_possible(piece, command.source, command.target):
                    pass
                if isinstance(command.source, CoastalTerritory):
                    if command.source.identified_coasts and isinstance(piece, Fleet):
                        if not self._share_identified_coast_border(piece.identified_coast, command.target):
                            command.result = "invalid"
                if not self._share_border(command.source, command.target):
                    command.result = "invalid"
                if isinstance(piece, Fleet):
                    if self._both_coastal(command.source, command.target):
                        if not self._share_coast(command.source, command.target):
                            command.result = "invalid"
            resolved_commands.append(command)
        return resolved_commands

    def _convoy_is_possible(self, piece, t1, t2):
        return isinstance(t1, CoastalTerritory) and \
                isinstance(t2, CoastalTerritory) and \
                isinstance(piece, Army)

    def _both_coastal(self, t1, t2):
        return isinstance(t1, CoastalTerritory) and \
                isinstance(t2, CoastalTerritory)

    def _share_border(self, t1, t2):
        for border in self.borders:
            if (t1 in border.territories) and (t2 in border.territories):
                return True
        return False

    def _share_identified_coast_border(self, coast, territory):
        for border in self.identified_coast_borders:
            if (coast == border.identified_coast) and (territory == border.territory):
                return True
        return False

    def _share_coast(self, t1, t2):
        for border in self.borders:
            if (t1 in border.territories) and (t2 in border.territories) and border.shared_coast:
                return True
        return False

    def _get_friendly_piece_from_territory(self, nation, territory):
        return [p for p in self.pieces if \
                p.territory == territory and p.nation == nation][0]

    def _friendly_piece_exists_in_territory(self, nation, territory):
        return any([p for p in self.pieces if \
                p.territory == territory and p.nation == nation])

