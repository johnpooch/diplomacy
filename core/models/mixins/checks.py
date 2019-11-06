"""
Mixin classes for ``Command`` which provide logic for determining whether a
command is legal.
"""
from django.utils.translation import gettext as _

from core.exceptions import IllegalCommandException
from core.models.base import CommandType, PieceType


class ChecksMixin:

    def check_illegal(self):
        """
        """
        # TODO make this magic
        try:
            if self.is_hold:
                self.check_hold_illegal()

            if self.is_move:
                self.check_move_illegal()

            if self.is_support:
                self.check_support_illegal()

            if self.is_convoy:
                self.check_convoy_illegal()

            if self.type == CommandType.BUILD:
                self.check_build_illegal()

        except IllegalCommandException as e:
            self.set_illegal(str(e))

    def check_hold_illegal(self):
        self._friendly_piece_exists_in_source(),

    def check_move_illegal(self):
        self._friendly_piece_exists_in_source(),
        self._target_not_same_as_source(),
        self._specifies_target_named_coast_if_fleet(),
        self._source_piece_can_reach_target(),

    def check_support_illegal(self):
        self._friendly_piece_exists_in_source(),
        self._aux_not_same_as_source(),
        self._source_piece_can_reach_target(),
        self._aux_piece_can_reach_target(),
        self._aux_occupied(),
        self._source_is_adjacent_to_target(),

    def check_convoy_illegal(self):
        self._friendly_piece_exists_in_source(),
        self._aux_occupied(),
        self._aux_piece_is_army(),
        self._aux_piece_can_reach_target(),
        self._source_piece_is_at_sea(),

    def check_retreat_illegal(self):
        self._friendly_piece_exists_in_source(),
        self._source_piece_can_reach_target(),
        self._specifies_target_named_coast_if_fleet(),
        self._piece_has_been_dislodged(),
        self._target_not_occupied(),
        self._target_not_where_attacker_came_from(),
        self._target_not_vacant_by_standoff_on_previous_turn(),

    def check_disband_illegal(self):
        self._friendly_piece_exists_in_source()

    def check_build_illegal(self):
        if self.target.occupied():
            raise IllegalCommandException(_(
                'Cannot build in occupied territory.'
            ))
            raise IllegalCommandException(_(
                'Cannot build in occupied territory.'
            ))
        if not self.target.has_supply_center():
            raise IllegalCommandException(_(
                'Cannot build in a territory that does not have a '
                'supply center.'
            ))
        if not self.target.supply_center.nationality == self.nation:
            raise IllegalCommandException(_(
                'Cannot build in supply centers outside of national '
                'borders.'
            ))
        if not self.target.controlled_by == self.nation:
            raise IllegalCommandException(_(
                'Cannot build in a supply center which is controlled '
                'by a foreign power.'
            ))
        if self.target.is_inland and \
                self.piece_type == PieceType.FLEET:
            raise IllegalCommandException(_(
                'Cannot build a fleet in an inland territory.'
            ))
        if self.target.is_complex and \
                self.piece_type == PieceType.FLEET and \
                not self.target_coast:
            raise IllegalCommandException(_(
                'Must specify a coast when building a fleet in a '
                'territory with named coasts.'
            ))

    def _friendly_piece_exists_in_source(self):
        if not self.source.friendly_piece_exists(self.nation):
            raise IllegalCommandException(_(
                f'No friendly piece exists in {self.source}.'
            ))
        return True

    def _target_not_same_as_source(self):
        if self.source == self.target:
            raise IllegalCommandException(_(
                f'{self.source.piece.type.title()} {self.source} cannot '
                'move to its own territory.'
            ))
        return True

    def _aux_not_same_as_source(self):
        if self.source == self.aux:
            raise IllegalCommandException(_(
                f'{self.source.piece.type.title()} {self.source} cannot '
                f'{self.type} its own territory.'
            ))
        return True

    def _source_piece_can_reach_target(self):
        try:
            target_coast = self.target_coast
        except AttributeError:
            target_coast = None
        # TODO refactor
        if not self.source.piece.can_reach(self.target, target_coast):
            if not target_coast:
                if self.source.is_complex:
                    raise IllegalCommandException(_(
                        f'{self.source.piece.type.title()} {self.source} '
                        f'({self.piece.named_coast.map_abbreviation}) cannot '
                        f'reach {self.target}.'
                    ))
                else:
                    raise IllegalCommandException(_(
                        f'{self.source.piece.type.title()} {self.source} cannot reach '
                        f'{self.target}.'
                    ))
            if self.target.is_complex and self.target_coast:
                raise IllegalCommandException(_(
                    f'{self.source.piece.type.title()} {self.source} cannot reach '
                    f'{self.target} ({self.target_coast.map_abbreviation}).'
                ))
                raise IllegalCommandException(_(
                    f'{self.source.piece.type.title()} {self.source} cannot reach '
                    f'{self.target}.'
                ))
        return True

    def _source_piece_is_at_sea(self):
        if not self.source.is_sea:
            raise IllegalCommandException(_(
                'Cannot convoy unless piece is at sea.'
            ))
        return True

    def _source_is_adjacent_to_target(self):
        if not self.source.adjacent_to(self.target):
            raise IllegalCommandException(_(
                'Cannot support to territory that is not adjacent to the '
                'supporting piece.'
            ))
        return True

    def _specifies_target_named_coast_if_fleet(self):
        """
        If the command piece is a fleet and the ``target`` is has named coasts,
        the command must specify a ``target_coast`` unless only one of the
        named coasts is within reach of the command piece, in which case the
        target coast is assumed to be that coast.
        """
        if self.target.is_complex \
                and self.source.piece.is_fleet \
                and not self.target_coast:
            # if more than one accessible coast there is ambiguity
            if len([nc for nc in self.target.named_coasts.all() if self.source
                    in nc.neighbours.all()]) > 1:
                raise IllegalCommandException(_(
                    'Cannot order an fleet into a territory with named coasts '
                    'without specifying a named coast.'
                ))
            else:
                self.target_coast = [nc for nc in self.target.named_coasts.all()
                                     if self.source in nc.neighbours.all()][0]
                self.save()
        return True

    def _aux_occupied(self):
        if not self.aux.occupied():
            raise IllegalCommandException(_(
                f'No piece exists in {self.aux}.'
            ))
        return True

    def _aux_piece_can_reach_target(self):
        if self.aux == self.target:
            return
        if not self.aux.piece.can_reach(self.target):
            raise IllegalCommandException(_(
                f'{self.aux.piece.type.title()} {self.aux} cannot '
                f'reach {self.target}.'
            ))
        return True

    def _aux_piece_is_army(self):
        if not self.aux.piece.is_army:
            raise IllegalCommandException(_(
                f'{self.piece.type.title()} {self.source} cannot '
                f'convoy piece at {self.aux} because it is a fleet.'
            ))
        return True

    def _aux_piece_move_legal(self):
        if self.aux.piece.command.is_move:
            self.aux.piece.command.check_illegal()
            if self.aux.piece.command.illegal:
                raise IllegalCommandException(_(
                    'Illegal because the command of '
                    f'{self.aux.piece.type.title()} {self.aux} is illegal.'
                ))
        return True

    def _piece_has_been_dislodged(self):
        if not self.source.piece.dislodged():
            raise IllegalCommandException(_(
                'Only pieces which have been dislodged can retreat.'
            ))
        return True

    def _target_not_occupied(self):
        if self.target.occupied():
            raise IllegalCommandException(_(
                'Dislodged piece cannot move to occupied territory.'
            ))
        return True

    def _target_not_where_attacker_came_from(self):
        if self.target == self.source.piece.dislodged_by\
                .get_previous_territory():
            raise IllegalCommandException(_(
                'Dislodged piece cannot move to territory from which '
                'attacking piece came.'
            ))
        return True

    def _target_not_vacant_by_standoff_on_previous_turn(self):
        if self.target.standoff_occured_on_previous_turn():
            raise IllegalCommandException(_(
                'Dislodged piece cannot move to territory where a standoff '
                'occured on the previous turn.'
            ))
        return True
