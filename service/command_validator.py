from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from service.models import Piece, Territory


# REFACTOR
class CommandValidator:

    def __init__(self, command):
        self.message = None
        self.nation = command.order.nation


class MoveValidator(CommandValidator):

    def __init__(self, command):
        super().__init__(command)
        self.source = command.source_territory
        self.target = command.target_territory
        self.source_coast = command.source_coast
        self.target_coast = command.target_coast

    def is_valid(self):
        if not self._friendly_piece_exists_in_source():
            raise ValidationError(_(
                'No friendly piece exists in the source territory.'
                )
            )

        if not self.target.accessible_by_piece_type(self.source.piece):
            raise ValidationError(_(
                'Target is not accessible by piece type.'
                )
            )
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
        super().is_valid()

        if not (self._target_adjacent_to_source() or self._convoy_is_possible()):
            raise ValidationError(_(
                'Army cannot move to non adjacent territory unless moving '
                'from one coastal territory to another coastal territory.'
                )
            )
        return True

    def _convoy_is_possible(self):
        return self._source_and_target_coastal()


class FleetMoveValidator(MoveValidator):

    def is_valid(self):
        super().is_valid()

        if self.source.is_complex():
            if self.target not in self.source_coast.neighbours.all():
                raise ValidationError(_(
                    'Fleet cannot move from a named coast to a territory '
                    'which is not a neighbour the named coast.'
                    )
                )

        if self.target.is_complex():
            if not self.target_coast:
                raise ValidationError(_(
                    'Fleet cannot move to complex territory without specifying a '
                    'named coast'
                    )
                )

            if self.source not in self.target_coast.neighbours.all():
                raise ValidationError(_(
                    'Fleet cannot move to a named coast which does not neighbour '
                    'the source territory.'
                    )
                )

        if not self._target_adjacent_to_source():
                raise ValidationError(_(
                    'Fleet cannot move to a non adjacent territory.'
                    )
                )

        if self._source_and_target_coastal() and \
                not self.source.shares_coast_with(self.target):
            raise ValidationError(_(
                'Fleet cannot move from one coastal territory to another '
                'unless both territories share a coastline.'
                )
            )
        return True


class SupportValidator(CommandValidator):

    def __init__(self, command):
        super().__init__(command)
        self.source = command.source_territory
        self.aux = command.aux_territory
        self.target = command.target_territory
        self.source_coast = command.source_coast
        self.target_coast = command.target_coast

    # NOTE can be simplified by simply asking can both the source and aux piece
    # reach the target.

    # Add a method to Piece which determines whether a territory can be reached.

    def is_valid(self):
        if not self._friendly_piece_exists_in_source():
            raise ValidationError(_(
                'No friendly piece exists in the source territory.'
                )
            )

        if not self.target.accessible_by_piece_type(self.source.piece):
            raise ValidationError(_(
                'Target is not accessible by supporting piece.'
                )
            )
        return True

    # TODO dry
    def _target_adjacent_to_source(self):
        return self.target in self.source.neighbours.all()

    # TODO dry
    def _target_adjacent_to_aux(self):
        return self.target in self.aux.neighbours.all()

    # TODO dry
    def _source_and_target_coastal(self):
        return (self.source.coastal and self.target.coastal)

    def _aux_and_target_coastal(self):
        return (self.aux.coastal and self.target.coastal)

    # TODO dry
    def _friendly_piece_exists_in_source(self):
        return Piece.objects.filter(
            territory=self.source,
            nation=self.nation
        ).exists()

    # TODO dry
    def _aux_convoy_is_possible(self):
        return self._aux_and_target_coastal() and self.aux.piece.is_army()

class ArmySupportValidator(SupportValidator):

    def is_valid(self):
        super().is_valid()

        if not (self._target_adjacent_to_source() or self._convoy_is_possible()):
            raise ValidationError(_(
                'Army cannot move to non adjacent territory unless moving '
                'from one coastal territory to another coastal territory.'
                )
            )
        return True

    # TODO dry
    def _convoy_is_possible(self):
        return self._source_and_target_coastal()


class FleetSupportValidator(SupportValidator):

    def is_valid(self):
        super().is_valid()

        if self.source.is_complex():
            if self.target not in self.source_coast.neighbours.all():
                raise ValidationError(_(
                    'Fleet cannot move from a named coast to a territory '
                    'which is not a neighbour the named coast.'
                    )
                )

        if self.target.is_complex():
            if not self.target_coast:
                raise ValidationError(_(
                    'Fleet cannot move to complex territory without specifying a '
                    'named coast'
                    )
                )

            if self.source not in self.target_coast.neighbours.all():
                raise ValidationError(_(
                    ''
                    )
                )

        if not self._target_adjacent_to_source():
            raise ValidationError(_(
                'Supporting fleet cannot support piece into a territory which '
                'is not adjacent to the supporting fleet.'
                )
            )

        if not self._target_adjacent_to_aux():
            # TODO refactor into single method
            if not self._aux_convoy_is_possible():
                raise ValidationError(_(
                    'Supporting fleet cannot support fleet into territory which is '
                    'not adjacent to the attacking fleet.'
                    )
                )

        if self._source_and_target_coastal() and \
                not self.source.shares_coast_with(self.target):
            raise ValidationError(_(
                'Fleet cannot move from one coastal territory to another '
                'unless both territories share a coastline.'
                )
            )
        return True


class NoPieceInSourceValidator:

    def is_valid(self):
        raise ValidationError(_(
            'No piece exists in this territory'
        )
    )


def get_command_validator(command):
    try:
        command.source_piece
    except Territory.piece.RelatedObjectDoesNotExist:
        return NoPieceInSourceValidator()
    if command.type == command.CommandType.MOVE:
        if command.source_piece.is_army():
            return ArmyMoveValidator(command)
        if command.source_piece.is_fleet():
            return FleetMoveValidator(command)

    if command.type == command.CommandType.SUPPORT:
        if command.source_piece.is_army():
            return ArmySupportValidator(command)
        if command.source_piece.is_fleet():
            return FleetSupportValidator(command)
