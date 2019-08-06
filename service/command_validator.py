from django.utils.translation import gettext as _

from service.models import Piece


class CommandValidator:

    def __init__(self, command):
        self.message = None
        self.nation = command.order.nation


class MoveValidator(CommandValidator):

    def __init__(self, command):
        super().__init__(command)
        self.source = command.source_territory
        self.target = command.target_territory
        self.named_coast = command.named_coast

    def is_valid(self):
        if not self._friendly_piece_exists_in_source():
            return False
        if not self.target.accessible_by_piece_type(self.source.piece):
            self.message = _('Target is not accessible by piece type.')
            return False
        return True

    def _target_adjacent_to_source(self):
        return self.target in self.source.neighbours.all()

    def _source_and_target_coastal(self):
        return (self.source.coastal and self.target.coastal)

    def _friendly_piece_exists_in_source(self):
        return Piece.objects.filter(
            territory=self.source,
            nation=self.nation
        ).exists()


class ArmyMoveValidator(MoveValidator):

    def is_valid(self):
        if not super().is_valid():
            return False

        if not (self._target_adjacent_to_source() or self._convoy_is_possible()):
            self.message = _(
                'Army cannot move to non adjacent territory unless moving '
                'from one coastal territory to another coastal territory.'
            )
            return False
        return True

    def _convoy_is_possible(self):
        return self._source_and_target_coastal()


class FleetMoveValidator(MoveValidator):

    def is_valid(self):
        if not super().is_valid():
            return False

        if self.target.is_complex() and not self.named_coast:
            self.message = _(
                'Fleet cannot move to complex territory without specifying a '
                'named coast'
            )
            return False

        if not self._target_adjacent_to_source():
            self.message = _('Fleet cannot move to non adjacent territory.')
            return False

        if self._source_and_target_coastal() and \
                not self.source.shares_coast_with(self.target):
            self.message = _(
                'Fleet cannot move from one coastal territory to another '
                'unless both territories share a coastline.'
            )
            return False
        return True


def get_command_validator(command):
    if command.type == command.CommandType.MOVE:
        if command.source_piece.is_army():
            return ArmyMoveValidator(command)
        if command.source_piece.is_fleet():
            return FleetMoveValidator(command)
