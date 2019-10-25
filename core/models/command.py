from copy import deepcopy

from django.apps import apps
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from core.models.base import CommandState, CommandType, DislodgedState, \
    HygenicModel, PieceType
from core.exceptions import IllegalCommandException


def debug_command(command):
    print('\n')
    print(command)
    if command.type == CommandType.MOVE:
        print(f'MAX ATTACK STRENGTH: {command.max_attack_strength}')
        print(f'MIN ATTACK STRENGTH: {command.min_attack_strength}')

        print(f'MAX DEFEND STRENGTH: {command.max_defend_strength}')
        print(f'MIN DEFEND STRENGTH: {command.min_defend_strength}')

        print(f'MAX PREVENT STRENGTH: {command.max_prevent_strength}')
        print(f'MIN PREVENT STRENGTH: {command.min_prevent_strength}')

        print(f'TERRITORY MAX HOLD STRENGTH: {command.target.max_hold_strength}')
        print(f'TERRITORY MIN HOLD STRENGTH: {command.target.min_hold_strength}')

        print(
            'OTHER ATTACKING PIECES: '
            f'{command.target.other_attacking_pieces(command.piece)}'
        )

        print(f'COMMAND OUTCOME: {command.state}')


class CommandQuerySet(models.QuerySet):

    @property
    def pieces(self):
        """

        """
        # TODO test
        Piece = apps.get_model('core', 'Piece')
        return Piece.objects.filter(command__in=self)


class CommandManager(models.Manager):
    """
    """
    def get_queryset(self):
        queryset = CommandQuerySet(self.model, using=self._db)
        return queryset

    def process_commands(self):
        """
        """
        all_commands_resolved = False
        qs = super().get_queryset()

        for command in qs:
            command.check_illegal()

        qs = super().get_queryset()

        # NOTE need to resolve all convoy commands first

        all_convoys_resolved = False
        while not all_convoys_resolved:
            # Need to find out if any convoys are dislodged. To do this we need
            # to resolve the moves and supports of all other fleets.
            fleet_commands = qs.filter(piece__type=PieceType.FLEET)\
                .exclude(illegal=True)
            convoy_commands = fleet_commands.filter(type=CommandType.CONVOY)

            for command in fleet_commands:
                if command.piece.dislodged_state == DislodgedState.UNRESOLVED:
                    command.piece.dislodged_decision()

            for command in fleet_commands:
                if not command.illegal \
                        and command.state == CommandState.UNRESOLVED:
                    command.resolve()

            for command in fleet_commands:
                command.save()
                # debug_command(command)

            fleet_commands = fleet_commands.filter(
                Q(state=CommandState.UNRESOLVED) |
                Q(piece__dislodged_state=DislodgedState.UNRESOLVED)
            )
            convoy_commands = convoy_commands.filter(
                Q(state=CommandState.UNRESOLVED) |
                Q(piece__dislodged_state=DislodgedState.UNRESOLVED)
            )

            if not convoy_commands:
                all_convoys_resolved = True

        while not all_commands_resolved:
            qs = qs.exclude(type=CommandType.CONVOY)

            for command in qs.exclude(illegal=True)\
                    .filter(state=CommandState.UNRESOLVED):
                if command.paradox_exists:
                    if command._min_attack_strength_result == command.min_attack_strength and command._max_attack_strength_result == command.max_attack_strength:
                        dependencies = command.get_attack_strength_dependencies()
                        for d in dependencies:
                            # NOTE hacky af
                            dependencies = qs.filter(id__in=[d.id for d in dependencies])
                            dependencies.update(state=CommandState.SUCCEEDS)

            for command in qs:
                if command.piece.dislodged_state == DislodgedState.UNRESOLVED:
                    command.piece.dislodged_decision()

            for command in qs:
                if not command.illegal \
                        and command.state == CommandState.UNRESOLVED:
                    command.resolve()

            if command.type == CommandType.MOVE:
                command._min_attack_strength_result = \
                    command.min_attack_strength
                command._max_attack_strength_result = \
                    command.max_attack_strength

                command._min_defend_strength_result = \
                    command.min_defend_strength
                command._max_defend_strength_result = \
                    command.max_defend_strength

                command._min_prevent_strength_result = \
                    command.min_prevent_strength
                command._max_prevent_strength_result = \
                    command.max_prevent_strength

                command._min_hold_strength_result = \
                    command.target.min_hold_strength
                command._max_hold_strength_result = \
                    command.target.max_hold_strength

            command.save()

            for command in qs:
                command.save()
                # debug_command(command)

            qs = qs.filter(
                Q(state=CommandState.UNRESOLVED) |
                Q(piece__dislodged_state=DislodgedState.UNRESOLVED)
            )

            if not qs:
                all_commands_resolved = True

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
            type=CommandType.CONVOY,
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
        choices=CommandType.CHOICES,
        default=CommandType.HOLD
    )
    state = models.CharField(
        max_length=15,
        null=False,
        choices=CommandState.CHOICES,
        default=CommandState.UNRESOLVED
    )
    source = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
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
        blank=True,
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
        choices=PieceType.CHOICES,
    )
    # TODO add invalid and invlaid message fields. Also add help text to
    # explain difference.
    illegal = models.BooleanField(
        default=False
    )
    illegal_message = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    success = models.BooleanField(default=True)
    bounced = models.BooleanField(default=False)
    # Outcome in human friendly terms
    result_message = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    # TODO explore whether these can be made into non db values
    _min_attack_strength_result = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    _max_attack_strength_result = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    _min_defend_strength_result = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    _max_defend_strength_result = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    _min_prevent_strength_result = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    _max_prevent_strength_result = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    _min_hold_strength_result = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    _max_hold_strength_result = models.PositiveIntegerField(
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
        try:
            if self.piece.type == PieceType.ARMY:
                if self.target_coast:
                    raise ValueError('Army command cannot specify a target coast.')
        except AttributeError:
            pass
        try:
            if self.piece.type == PieceType.ARMY:
                if self.type == CommandType.CONVOY:
                    raise ValueError('Army cannot convoy.')
        except AttributeError:
            pass

    @property
    def paradox_exists(self):
        # TODO test
        # TODO refactor
        """
        Paradox exists if none of the values have changed from the previous
        iteration of the loop.
        """
        if self.type == CommandType.MOVE:
            return all([
                self._min_attack_strength_result == self.min_attack_strength,
                self._max_attack_strength_result == self.max_attack_strength,
                self._min_defend_strength_result == self.min_defend_strength,
                self._max_defend_strength_result == self.max_defend_strength,
                self._min_prevent_strength_result == self.min_prevent_strength,
                self._max_prevent_strength_result == self.max_prevent_strength,
                self._min_hold_strength_result == self.target.min_hold_strength,
                self._max_hold_strength_result == self.target.max_hold_strength,
            ])

    def check_illegal(self):
        """
        Checks if a given command is illegal.
        """
        try:
            if self.type == CommandType.HOLD:
                self._friendly_piece_exists_in_source(),

            if self.type == CommandType.MOVE:
                [
                    self._friendly_piece_exists_in_source(),
                    self._target_not_same_as_source(),
                    self._specifies_target_named_coast_if_fleet(),
                    self._source_piece_can_reach_target(),
                ]
            if self.type == CommandType.SUPPORT:
                [
                    self._friendly_piece_exists_in_source(),
                    self._aux_not_same_as_source(),
                    self._source_piece_can_reach_target(),
                    self._source_piece_can_reach_target(),
                    self._aux_occupied(),
                    # self._aux_piece_can_reach_target(),
                    # self._aux_piece_move_legal(),
                ]
            if self.type == CommandType.CONVOY:
                [
                    self._friendly_piece_exists_in_source(),
                    self._aux_occupied(),
                    self._aux_piece_is_army(),
                    self._aux_piece_can_reach_target(),
                    self._source_piece_is_at_sea(),
                    # self._aux_piece_move_legal(),
                ]
            if self.type == CommandType.RETREAT:
                [
                    self._friendly_piece_exists_in_source(),
                    self._source_piece_can_reach_target(),
                    self._specifies_target_named_coast_if_fleet(),
                    self._piece_has_been_dislodged(),
                    self._target_not_occupied(),
                    self._target_not_where_attacker_came_from(),
                    self._target_not_vacant_by_standoff_on_previous_turn(),
                ]
            if self.type == CommandType.DISBAND:
                self._friendly_piece_exists_in_source()

            if self.type == CommandType.BUILD:
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
                if self.target.is_inland() and \
                        self.piece_type == PieceType.FLEET:
                    raise IllegalCommandException(_(
                        'Cannot build a fleet in an inland territory.'
                    ))
                if self.target.is_complex() and \
                        self.piece_type == PieceType.FLEET and \
                        not self.target_coast:
                    raise IllegalCommandException(_(
                        'Must specify a coast when building a fleet in a '
                        'territory with named coasts.'
                    ))
        except IllegalCommandException as e:
            self.set_illegal(str(e))

    def set_illegal(self, message):
        """
        Helper to
        """
        self.illegal = True
        self.illegal_message = message
        self.set_fails()

    def set_succeeds(self, save=True):
        """
        """
        self.state = CommandState.SUCCEEDS
        if save:
            self.save()

    def set_fails(self):
        """
        """
        self.state = CommandState.FAILS
        self.save()

    @property
    def unresolved(self):
        """
        """
        return self.state == CommandState.UNRESOLVED

    @property
    def succeeds(self):
        """
        """
        return self.state == CommandState.SUCCEEDS

    @property
    def fails(self):
        """
        """
        return self.state == CommandState.FAILS

    @property
    def move_path(self):
        """
        Determine whether a move command has a path to the target.

        The path of a move command is successful when the origin and
        destination of the move command are adjacent and accessible by the
        moving piece type, or when there is a chain of adjacent fleets from
        origin to destination each with a matching and successful convoy order.
        """
        if self.type != CommandType.MOVE:
            raise ValueError(
                '`move_path` method can only be used on move commands.'
            )
        if self.source.piece.is_fleet():
            # if moving from named coast, ensure target is neighbour of coast
            if self.source.piece.named_coast:
                return self.target in self.source.piece.named_coast.neighbours.all()

            # if moving from one coast to another, check shared coast
            if self.source.coastal and self.target.coastal:
                return self.target in self.source.shared_coasts.all()

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
            if not any([c.piece.dislodged for c in path]):
                return True
        return False

    def head_to_head_exists(self):
        """
        Determine whether the piece in the target territory of a move command
        is moving to the source of this command, i.e. two pieces are trying to
        move into eachother's territories.
        """
        if not self.type == CommandType.MOVE:
            raise ValueError(
                'Only move commands can be in head to head battles.'
            )

        if not self.target.occupied():
            return False

        if not self.target.piece.command.type == CommandType.MOVE:
            return False

        if self.target.piece.command.target == self.source:
            if self.target.piece.command.move_path:
                self.head_to_head_opposing_piece = self.target.piece
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

              A MOVE decision of a unit ordered to move results in 'moves' when:

            The minimum of the ATTACK STRENGTH is larger than the maximum of
            the DEFEND STRENGTH of the opposing unit in case of a head to head
            battle or otherwise larger than the maximum of the HOLD STRENGTH of
            the attacked area. And in all cases the minimum of the ATTACK
            STRENGTH is larger than the maximum of the PREVENT STRENGTH of all
            of the units moving to the same area.

            A MOVE decision of a unit ordered to move results in 'fails' when:

            The maximum of the ATTACK STRENGTH is smaller than or equal to the
            minimum of the DEFEND STRENGTH of the opposing unit in case of a
            head to head battle or otherwise smaller than or equal to the
            minimum of the HOLD STRENGTH of the attacked area. Or the maximum
            of the ATTACK STRENGTH is smaller than or equal to the minimum of
            the PREVENT STRENGTH of at least one of the units moving to the
            same area.

            In all other cases a MOVE decision of a unit ordered to move
            remains 'undecided'.
        """
        if self.check_illegal():
            self.illegal_move = True
            return self.set_fails()

        if not self.unresolved:
            raise ValueError(
                'Cannot call `resolve()` on a command which is already resolved.'
            )

        if self.type == CommandType.MOVE:
            # succeeds if...
            if self.head_to_head_exists():
                opposing_unit = self.target.piece
                if self.min_attack_strength > opposing_unit.command.max_defend_strength:
                    if self.min_attack_strength > max(
                            [p.command.max_prevent_strength
                             for p in self.target.other_attacking_pieces(self.piece)]
                    ):
                        return self.set_succeeds()
            if self.target.other_attacking_pieces(self.piece):
                if self.min_attack_strength > self.target.max_hold_strength:
                    if self.min_attack_strength > max(
                        [p.command.max_prevent_strength
                         for p in self.target.other_attacking_pieces(self.piece)]
                    ):
                        return self.set_succeeds()
            else:
                if self.min_attack_strength > self.target.max_hold_strength:
                    return self.set_succeeds()

            # fails if...
            if self.head_to_head_exists():
                opposing_unit = self.target.piece
                if self.max_attack_strength <= opposing_unit.command.min_defend_strength:
                    return self.set_fails()
            if self.max_attack_strength <= self.target.min_hold_strength:
                return self.set_fails()
            if self.target.other_attacking_pieces(self.piece):
                if self.max_attack_strength <= min(
                    [p.command.min_prevent_strength
                     for p in self.target.other_attacking_pieces(self.piece)]
                ):
                    return self.set_fails()

        if self.type == CommandType.SUPPORT:
            # TODO refactor
            # succeeds if...
            if not self.source.attacking_pieces:
                self.set_succeeds()
            if self.source.piece.sustains:
                if self.target.occupied() and self.aux.occupied():
                    if self.aux.piece.command.type == CommandType.MOVE and \
                            self.aux.piece.command.target == self.target:
                        if all([p.command.max_attack_strength == 0
                                for p in self.source.other_attacking_pieces
                                (self.target.piece)]):
                            self.set_succeeds()
                if all([p.command.max_attack_strength == 0
                        for p in self.source.attacking_pieces]):
                    self.set_succeeds()

            # fails if...
            # If aux piece is not going to target of command
            if self.aux.occupied():
                if self.aux.piece.command.type == CommandType.MOVE \
                        and self.aux.piece.command.target != self.target \
                        and not self.aux.piece.command.illegal:
                    self.set_fails()
            # If aux piece holds and support target is not same as aux
            if self.aux.piece.command.type in [CommandType.HOLD, CommandType.CONVOY, CommandType.SUPPORT] and self.target != self.aux:
                self.set_fails()

            if self.target.occupied():
                if self.target != self.aux and self.target.piece.nation == self.nation:
                    if (self.target.piece.command.type == CommandType.MOVE and self.target.piece.command.fails) or (self.target.piece.command.type in [CommandType.HOLD, CommandType.SUPPORT, CommandType.CONVOY]):
                        self.set_fails()
            if self.source.piece.dislodged:
                self.set_fails()
            if self.target.occupied() and self.aux.occupied():
                if self.aux.piece.command.type == CommandType.MOVE and \
                        self.aux.piece.command.target == self.target:
                    if any([p.command.min_attack_strength >= 1
                            for p in self.source.other_attacking_pieces
                            (self.target.piece)]):
                        self.set_fails()

                    else:
                        return
            if self.source.attacking_pieces and \
                    any([p.command.min_attack_strength >= 1
                         for p in self.source.attacking_pieces
                         if p.territory != self.aux.piece.command.target]):
                self.set_fails()

        if self.type == CommandType.HOLD:
            if self.piece.sustains:
                self.set_succeeds()
            if self.piece.dislodged:
                self.set_fails()

        if self.type == CommandType.CONVOY:
            # if unmatched
            if not self.aux.piece.command.target == self.target:
                self.set_fails()
            # TODO somehow set fails if not part of successful convoy path
            if self.piece.dislodged:
                self.set_fails()
            if self.piece.sustains:
                self.set_succeeds()

    def get_attack_strength_dependencies(self, dependencies=[]):
        """
        """
        # TODO test
        if self not in dependencies:
            dependencies.append(self)
        else:
            return dependencies
        if self.target.piece:
            if self.target.piece.command.unresolved:
                for c in self.target.piece.command.get_attack_strength_dependencies(dependencies):
                    if c not in dependencies:
                        dependencies.append(c)
        return dependencies

    @property
    def min_attack_strength(self):
        """
        Determine the minimum attack strength of a command.
        """
        if not self.type == CommandType.MOVE:
            raise ValueError(
                'Attack strength should only be calculated for move commands.'
            )
        if not self.move_path:
            return 0
        if self.target.occupied():
            if self.head_to_head_exists() or \
                    self.target.piece.command.type != CommandType.MOVE or \
                    (not self.target.piece.command.succeeds):
                if self.target.piece.nation == self.nation:
                    return 0
                return 1 + len([c for c in self.supporting_commands if c.succeeds and 
                                c.nation != self.target.piece.nation])
            return 1 + len([c for c in self.supporting_commands if c.succeeds and 
                            c.nation != self.target.piece.nation])
        return 1 + len([c for c in self.supporting_commands if c.succeeds])

    @property
    def max_attack_strength(self):
        """
        """
        if not self.type == CommandType.MOVE:
            raise ValueError(
                'Attack strength should only be calculated for move commands.'
            )
        if not self.move_path:
            return 0
        if self.target.occupied():
            if self.head_to_head_exists() or \
                    self.target.piece.command.type != CommandType.MOVE or \
                    self.target.piece.command.fails:
                if self.target.piece.nation == self.nation:
                    return 0
                return 1 + len([c for c in self.supporting_commands if (not c.fails) and
                                c.nation != self.target.piece.nation])
            return 1 + len([c for c in self.supporting_commands if (not c.fails) and
                            c.nation != self.target.piece.nation])
        return 1 + len([c for c in self.supporting_commands if (not c.fails)])

    @property
    def min_defend_strength(self):
        """
        """
        if not self.type == CommandType.MOVE:
            raise ValueError(
                'Defend strength should only be calculated for move commands.'
            )
        return 1 + len([c for c in self.supporting_commands
                        if c.succeeds])

    @property
    def max_defend_strength(self):
        """
        """
        if not self.type == CommandType.MOVE:
            raise ValueError(
                'Defend strength should only be calculated for move commands.'
            )
        return 1 + len([c for c in self.supporting_commands
                        if not c.fails])

    @property
    def min_prevent_strength(self):
        """
        """
        # NOTE need to add unresolved to path
        if not self.move_path:
            return 0
        if self.head_to_head_exists():
            opposing_unit = self.target.piece
            if not opposing_unit.command.fails:
                return 0
        return 1 + len([c for c in self.supporting_commands if c.succeeds])

    @property
    def max_prevent_strength(self):
        """
        """
        # NOTE need to add unresolved to path
        if not self.move_path:
            return 0
        if self.head_to_head_exists():
            opposing_unit = self.target.piece
            if opposing_unit.command.succeeds:
                return 0
        return 1 + len([c for c in self.supporting_commands if not c.fails])

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
        if self.type != CommandType.SUPPORT:
            raise ValueError('Only `support` commands can be cut.')

        if self.source.piece.dislodged:
            return True

        foreign_attacking_pieces = self.source\
            .foreign_attacking_pieces(self.nation)

        for attacker in foreign_attacking_pieces:
            if attacker.command.move_path and \
                    attacker.territory != self.aux.piece.command.target:
                return True
        return False

    @property
    def supporting_commands(self):
        # TODO test
        """
        """
        if self.type == CommandType.MOVE:
            if not self.illegal:
                return Command.objects.filter(
                    aux=self.source,
                    target=self.target,
                    type=CommandType.SUPPORT,
                )
        return Command.objects.filter(
            aux=self.source,
            target=self.source,
            type=CommandType.SUPPORT,
        )

    @property
    def successful_supporting_commands(self):
        """
        """
        return self.supporting_commands.filter(illegal=False)

    @property
    def nation(self):
        """
        Helper to get the nation of a command more easily.
        """
        return self.order.nation

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
                if self.source.is_complex():
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
            if self.target.is_complex() and self.target_coast:
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
        if not self.source.is_sea():
            raise IllegalCommandException(_(
                'Cannot convoy unless piece is at sea.'
            ))
        return True

    def _specifies_target_named_coast_if_fleet(self):
        """
        If the command piece is a fleet and the ``target`` is has named coasts,
        the command must specify a ``target_coast`` unless only one of the
        named coasts is within reach of the command piece, in which case the
        target coast is assumed to be that coast.
        """
        if self.target.is_complex() \
                and self.source.piece.is_fleet() \
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
        if not self.aux.piece.can_reach(self.target):
            raise IllegalCommandException(_(
                f'{self.aux.piece.type.title()} {self.aux} cannot '
                f'reach {self.target}.'
            ))
        return True

    def _aux_piece_is_army(self):
        if not self.aux.piece.is_army():
            raise IllegalCommandException(_(
                f'{self.piece.type.title()} {self.source} cannot '
                f'convoy piece at {self.aux} because it is a fleet.'
            ))
        return True

    def _aux_piece_move_legal(self):
        if self.aux.piece.command.type == CommandType.MOVE:
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
