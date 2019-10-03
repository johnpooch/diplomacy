from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.models.base import HygenicModel
from core.models.piece import Piece


class CommandManager(models.Manager):
    """
    """

    def get_convoying_commands(self, source, target):
        """
        Get all commands which are convoying from ``source`` to ``target``.

        Args:
            * ``source`` - ``Territory``
            * ``target`` - ``Territory``

        Returns:
            * ``QuerySet`` of ``Command`` instances.
        """
        qs = super().get_queryset()
        return qs.filter(
            type=Command.Types.CONVOY,
            aux=source,
            target=target
        )

    def get_convoy_paths(self, source, target):
        """
        Gets a list of all available convoy paths from one territory to
        another.

        Args:
            * ``source`` - ``Territory``
            * ``target`` - ``Territory``

        Returns:
            * A ``list`` where each item in the list is a unique ``tuple`` of
            ``Command`` instances. Each ``tuple`` represents a possible convoy
            path.
        """
        convoy_paths = set()
        commands = self.get_convoying_commands(source, target)
        for command in commands:
            if command.source.adjacent_to(source):
                # if direct convoy
                if command.source.adjacent_to(target):
                    # add single command tuple to `convoy_paths`
                    path = (command,)
                    convoy_paths.add(path)
                else:
                    remaining = self.__all_other_commands(commands, command)
                    paths = self.__build_chain([command], target, remaining)
                    [convoy_paths.add(p) for p in paths]
        return list(convoy_paths)

    def __build_chain(self, initial_chain, target, commands):
        """
        Recursive method which attempts to build a chain of convoying commands
        to a given ``target``.
        """
        complete_chains = []
        for command in commands:
            # if command neigbouring last node in chain, add command to chain
            if command.source.adjacent_to(initial_chain[-1].source):
                chain = initial_chain + [command]

                # path found - neighbouring piece is adjacent to target
                if command.source.adjacent_to(target):
                    complete_chains.append(tuple(chain))
                    continue

                # path not found - check new node's neighbours (recurse)
                remaining = self.__all_other_commands(commands, command)
                inner_chains = self.__build_chain(chain, target, remaining)

                # if the inner method returns complete chains, add them to
                # outer method's complete chains
                if inner_chains:
                    complete_chains.append(inner_chains[0])

        if complete_chains:
            return complete_chains

    @staticmethod
    def __all_other_commands(commands, command_to_remove):
        """
        Helper method to get a copy of a list containing all commands other
        than the given ``command``.
        """
        remaining_commands = list(deepcopy(commands))
        remaining_commands.remove(command_to_remove)
        return remaining_commands


class Command(HygenicModel):
    """
    """

    class Types:
        HOLD = 'hold'
        MOVE = 'move'
        SUPPORT = 'support'
        CONVOY = 'convoy'
        RETREAT = 'retreat'
        BUILD = 'build'
        DISBAND = 'disband'
        CHOICES = (
            (HOLD, 'Hold'),
            (MOVE, 'Move'),
            (SUPPORT, 'Support'),
            (CONVOY, 'Convoy'),
            (RETREAT, 'Retreat'),
            (BUILD, 'Build'),
            (DISBAND, 'Disband')
        )

    class CommandStates:
        UNRESOLVED = 'unresolved'
        SUCCEEDS = 'succeeds'
        FAILS = 'fails'
        CHOICES = (
            (UNRESOLVED, 'Unresolved'),
            (SUCCEEDS, 'Succeeds'),
            (FAILS, 'Fails')
        )

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='+',
        db_column="order_id",
        null=False
    )
    type = models.CharField(
        max_length=8,
        null=False,
        choices=Types.CHOICES,
        default=Types.HOLD
    )
    state = models.CharField(
        max_length=15,
        null=False,
        choices=CommandStates.CHOICES,
        default=CommandStates.UNRESOLVED
    )
    source = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=True
    )
    piece = models.OneToOneField(
        'Piece',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    target = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
    )
    target_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )
    aux = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
    )
    # Only used on build commands
    piece_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=Piece.PieceType.CHOICES,
    )
    valid = models.BooleanField(default=True)
    success = models.BooleanField(default=True)
    # Outcome in human friendly terms
    result_message = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    objects = CommandManager()

    class Meta:
        db_table = 'command'

    def __str__(self):
        return f'{self.source.piece.type} {self.source} {self.type}'

    def clean(self):
        """
        """
        if self.type == self.Types.HOLD:
            self._friendly_piece_exists_in_source(),

        if self.type == self.Types.MOVE:
            [
                self._friendly_piece_exists_in_source(),
                self._source_piece_can_reach_target(),
                self._specifies_target_named_coast_if_fleet(),
            ]
        if self.type == self.Types.SUPPORT:
            [
                self._friendly_piece_exists_in_source(),
                self._source_piece_can_reach_target(),
                self._aux_occupied(),
                self._aux_piece_can_reach_target(),
            ]
        if self.type == self.Types.CONVOY:
            [
                self._friendly_piece_exists_in_source(),
                self._aux_occupied(),
                self._aux_piece_can_reach_target(),
                self._source_piece_is_at_sea(),
            ]
        if self.type == self.Types.RETREAT:
            [
                self._friendly_piece_exists_in_source(),
                self._source_piece_can_reach_target(),
                self._specifies_target_named_coast_if_fleet(),
                self._piece_has_been_dislodged(),
                self._target_not_occupied(),
                self._target_not_where_attacker_came_from(),
                self._target_not_vacant_by_standoff_on_previous_turn(),
            ]
        if self.type == self.Types.DISBAND:
            self._friendly_piece_exists_in_source()

        if self.type == self.Types.BUILD:
            # check territory is not occupied
            if self.target.occupied():
                raise ValidationError(_(
                    'Cannot build in occupied territory.'
                ))
            # check target territory has supply center
            if not self.target.has_supply_center():
                raise ValidationError(_(
                    'Cannot build in a territory that does not have a supply '
                    'center.'
                ))
            # check target territory nationality
            if not self.target.supply_center.nationality == self.nation:
                raise ValidationError(_(
                    'Cannot build in supply centers outside of home territory.'
                ))
            # check target territory nationality
            if not self.target.controlled_by == self.nation:
                raise ValidationError(_(
                    'Cannot build in supply centers which are not controlled by '
                    'nation.'
                ))
            # cannot build fleet inland
            if self.target.is_inland() and \
                    self.piece_type == Piece.PieceType.FLEET:
                raise ValidationError(_(
                    'Cannot build fleet in inland territory.'
                ))

    def succeed(self):
        """
        """
        self.state = self.CommandStates.SUCCEDED
        self.save()

    def fail(self):
        """
        """
        self.state = self.CommandStates.FAILED
        self.save()

    @property
    def succeeded(self):
        """
        """
        return self.state == self.CommandStates.SUCCEEDED

    @property
    def failed(self):
        """
        """
        return self.state == self.CommandStates.FAILED

    @property
    def move_path(self):
        """
        Determine whether a move command has a path to the target.

        The path of a move command is successful when the origin and
        destination of the move command are adjacent and accessible by the
        moving piece type, or when there is a chain of adjacent fleets from
        origin to destination each with a matching and successful convoy order.
        """
        if self.type != self.Types.MOVE:
            raise ValueError(
                '`move_path` method can only be used on move commands.'
            )
        if self.source.piece.is_fleet():
            # if moving from named coast, ensure target is neighbour of coast
            if self.source.piece.named_coast:
                return self.target in self.source.piece.named_coast.neighbours.all()

            # if moving from one coast to another, check shared coast
            if self.source.coastal and self.target.coastal:
                return self.target in self.territory.shared_coasts.all()

        # check adjacent to target and accessible by piece type
        if self.source.adjacent_to(self.target) and \
                self.target.accessible_by_piece_type(self.source.piece):
            return True

        # if not adjacent, check for convoy
        if self.source.piece.is_army():
            if self.source.coastal and self.target.coastal:
                return self.successful_convoy_exists
        return False

    @property
    def successful_convoy_exists(self):
        """
        Determines whether a successful convoy exists between ``source`` and
        ``target``.
        """
        convoy_paths = self.__class__.objects\
            .get_convoy_paths(self.source, self.target)
        for path in convoy_paths:
            if not any([c.source.piece.dislodged for c in path]):
                return True
        return False

    def resolve(self):
        """
        MOVE:
            - In case of a head-to-head battle, the move succeeds when the
              attack strength is larger then the defend strength of the
              opposing unit and larger than the prevent strength of any unit
              moving to the same area. If one of the opposing strengths is
              equal or greater, then the move fails.

            - If there is no head-to-head battle, the move succeeds when the
              attack strength is larger then the hold strength of the
              destination and larger than the prevent strength of any unit
              moving to the same area. If one of the opposing strengths is
              equal or greater, then the move fails.
        """
        # if self.type == self.Types.MOVE:
        #     if False:  # head-to-head battle
        #         if self.attack_strength > opposing_unit.defend_strength and \
        #                 self.attack_strength > max([unit.prevent_strength for unit in units]):
        #             return self.succeed()
        #         return self.failed()
        #     else:
        #         if self.attack_strength > self.target.hold_strength and \
        #                 self.attack_strength > max([unit.prevent_strength for unit in units]):
        #             return self.succeed()
        #         return self.failed()
        pass

#     @property
#     def attack_strength(self):
#         """
#         - If the path of the move order is not successful, then the attack
#           strength is 0.

#         - Otherwise, if the destination is empty, or in a case where there
#           is no head-to-head battle and the unit at the destination has a
#           move order for which the move is successful, then the attack
#           strength is 1 plus the number of successful support orders.

#         - If not and the unit at the destination is of the same
#           nationality, then the attack strength is 0.

#         - In all other cases, the attack strength is 1 plus the number of
#           successful support orders of units that do not have the same
#           nationality as the unit at the destination.
#         """
#         if not self.path or \
#                 self.target.piece.nationality == self.nationality:
#             return 0

#         if not self.target.piece or \
#                 (self.target.no_head_to_head and
#                  self.target.piece.command.state == self.CommandStates.SUCCEEDED and
#                  self.target.piece.command.type == 'MOVE'):
#             return 1 + self.support

#         return 1 + len([s for s in self.supporting_pieces
#                         if s.nationality != self.target.piece.nationality])

    @property
    def cut(self):
        """
        Determine whether a support command has been cut. Other types of
        command cannot be cut.

        A support order is cut when another unit is ordered to move to the area
        of the supporting unit and the following conditions are satisfied:

          - The moving unit is of a different nationality
          - The destination of the supported unit is not the area of the unit
            attacking the support
          - The moving unit has a successful path
          - A support is also cut when it is dislodged.
        """
        if self.type != self.Types.SUPPORT:
            raise ValueError('Only `support` commands can be cut.')

        if self.source.piece.dislodged:
            return True

        foreign_attacking_pieces = self.source\
            .foreign_attacking_pieces(self.nation)

        for attacker in foreign_attacking_pieces:
            if attacker.path and \
                    attacker.territory != self.aux.piece.command.target:
                return True
        return False

    @property
    def nation(self):
        """
        Helper to get the nation of a command more easily.
        """
        return self.order.nation

    def _friendly_piece_exists_in_source(self):
        if not self.source.friendly_piece_exists(self.nation):
            raise ValidationError(_(
                f'No friendly piece exists in {self.source}.'
            ))
        return True

    def _source_piece_can_reach_target(self):
        try:
            target_coast = self.target_coast
        except AttributeError:
            target_coast = None
        if not self.source.piece.can_reach(self.target, target_coast):
            raise ValidationError(_(
                f'{self.source.piece.type.title()} {self.source} cannot reach '
                f'{self.target}.'
            ))
        return True

    def _source_piece_is_at_sea(self):
        if not self.source.is_sea():
            raise ValidationError(_(
                'Cannot convoy unless piece is at sea.'
            ))
        return True

    def _specifies_target_named_coast_if_fleet(self):
        if self.target.is_complex() \
                and self.source.piece.is_fleet() \
                and not self.target_coast:
            raise ValidationError(_(
                'Cannot order an fleet into a complex territory without '
                'specifying a named coast.'
            ))
        return True

    def _aux_occupied(self):
        if not self.aux.occupied():
            raise ValidationError(_(
                f'No piece exists in {self.aux}.'
            ))
        return True

    def _aux_piece_can_reach_target(self):
        if not self.aux.piece.can_reach(self.target):
            raise ValidationError(_(
                f'{self.aux.piece.type.title()} {self.aux} cannot '
                f'reach {self.target}.'
            ))
        return True

    def _piece_has_been_dislodged(self):
        if not self.source.piece.dislodged():
            raise ValidationError(_(
                'Only pieces which have been dislodged can retreat.'
            ))
        return True

    def _target_not_occupied(self):
        if self.target.occupied():
            raise ValidationError(_(
                'Dislodged piece cannot move to occupied territory.'
            ))
        return True

    def _target_not_where_attacker_came_from(self):
        if self.target == self.source.piece.dislodged_by\
                .get_previous_territory():
            raise ValidationError(_(
                'Dislodged piece cannot move to territory from which '
                'attacking piece came.'
            ))
        return True

    def _target_not_vacant_by_standoff_on_previous_turn(self):
        if self.target.standoff_occured_on_previous_turn():
            raise ValidationError(_(
                'Dislodged piece cannot move to territory where a standoff '
                'occured on the previous turn.'
            ))
        return True
