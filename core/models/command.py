from copy import deepcopy

from django.apps import apps
from django.db import models

from core.models.base import CommandState, CommandType, HygenicModel, PieceType
from core.models.mixins.checks import ChecksMixin
from core.models.mixins.decisions import CommandDecisionsMixin
from core.models.mixins.resolver import ResolverMixin


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
            'SUPPORTING COMMANDS: '
            f'{command.supporting_commands}'
        )
        print(
            'OTHER ATTACKING PIECES: '
            f'{command.target.other_attacking_pieces(command.piece)}'
        )

    if command.illegal:
        print(f'COMMAND ILLEGAL MESSAGE: {command.illegal_message}')
    print(f'COMMAND OUTCOME: {command.state}')


class CommandQuerySet(models.QuerySet):

    @property
    def pieces(self):
        """
        """
        # TODO test
        Piece = apps.get_model('core', 'Piece')
        return Piece.objects.filter(command__in=self)


# NOTE this shouldn't be used for everything, only when processing the
# commands.
class CommandManager(models.Manager):
    """
    """
    def get_queryset(self):
        queryset = CommandQuerySet(self.model, using=self._db)
        # TODO move to QS
        queryset = queryset.select_related(
            'order__nation_state',
            'source__piece__nation',
            'aux__piece',
            'target__piece__nation',
            'target_coast',
            'piece',
        ).prefetch_related(
            'source__neighbours',
            'source__shared_coasts',
            'source__named_coasts',
            'source__piece__named_coast__neighbours',
            'aux__neighbours',
            'aux__shared_coasts',
            'aux__named_coasts',
            'target__neighbours',
            'target__shared_coasts',
            'target__named_coasts',
        )
        return queryset

    def process(self):
        """
        Processes all commands in a game.
        """
        # determine whether any commands are illegal
        # NOTE needs to be updated to do correctgame and turn
        all_commands = list(self.get_queryset())
        for command in all_commands:
            command.check_illegal()

        # resolve convoy commands first
        unresolved_fleet_commands = [c for c in all_commands if c.piece.is_fleet]
        self.__resolve_commands(unresolved_fleet_commands, convoys_only=True)

        # resolve all other commands
        unresolved_commands = [c for c in all_commands if c.unresolved]
        self.__resolve_commands(unresolved_commands)

        # TODO improve
        # check all pieces dislodged decision
        [c.piece.dislodged_decision() for c in all_commands if c.piece.unresolved]

        [c.save() for c in all_commands]

    def __resolve_commands(self, unresolved_commands, convoys_only=False):
        """
        """
        # determine whether any convoys are dislodged. This means resolving
        # move and support commands of all other fleets
        resolved_commands = []
        while True:

            # NOTE I have to do this because changing an attribute on the piece
            # doesn't get reflected when the piece is accessed again from the
            # command. There must be a work around for this.
            [c.refresh_from_db() for c in unresolved_commands]

            for command in unresolved_commands:
                if command.piece.unresolved:
                    command.piece.dislodged_decision()

            for command in unresolved_commands:
                if command.unresolved:
                    command.resolve()

            # print(debug_command(command))

            # get resolved_commands
            [resolved_commands.append(c) for c in unresolved_commands
             if not (c.unresolved or c.piece.unresolved)]

            # filter out resolved commands
            unresolved_commands = [c for c in unresolved_commands if
                                   c.unresolved or c.piece.unresolved]

            # return if there are no more unresolved commands
            if convoys_only:
                if not [c for c in unresolved_commands if c.is_convoy]:
                    return
            else:
                if not unresolved_commands:
                    return

    def get_convoying_commands(self, source, target):
        """
        Get all legal commands which are convoying from ``source`` to
        ``target``.

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
            target=target,
            illegal=False
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
                    if paths:
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


class Command(HygenicModel, ChecksMixin, CommandDecisionsMixin, ResolverMixin):
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
    # TODO helptext
    via_convoy = models.BooleanField(
        default=False
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

    objects = CommandManager()

    class Meta:
        db_table = 'command'

    def __str__(self):
        return f'{self.source.piece.type} {self.source} {self.type}'

    def clean(self):
        """
        """
        try:
            if self.piece.is_army:
                if self.target_coast:
                    raise ValueError('Army command cannot specify a target coast.')
                if self.type == CommandType.CONVOY:
                    raise ValueError('Army cannot convoy.')
        except AttributeError:
            pass

    def set_illegal(self, message):
        self.illegal = True
        self.illegal_message = message
        self.set_fails()

    # NOTE these two shouldn't save
    def set_succeeds(self, save=True):
        self.state = CommandState.SUCCEEDS
        if save:
            self.save()

    def set_fails(self):
        self.state = CommandState.FAILS
        self.save()

    @property
    def unresolved(self):
        return self.state == CommandState.UNRESOLVED

    @property
    def succeeds(self):
        return self.state == CommandState.SUCCEEDS

    @property
    def fails(self):
        return self.state == CommandState.FAILS

    @property
    def successful_support(self):
        return [c for c in self.supporting_commands if c.succeeds]

    @property
    def non_failing_support(self):
        return [c for c in self.supporting_commands if not c.fails]

    @property
    def successful_hold_support(self):
        return [c for c in self.hold_support if c.succeeds]

    @property
    def non_failing_hold_support(self):
        return [c for c in self.hold_support if not c.fails]

    @property
    def supporting_commands(self):
        # TODO test
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
    def hold_support(self):
        return Command.objects.filter(
            aux=self.source,
            target=self.source,
            type=CommandType.SUPPORT,
        )

    # TODO bin this
    @property
    def successful_supporting_commands(self):
        return self.supporting_commands.filter(illegal=False)

    @property
    def nation(self):
        return self.order.nation

    @property
    def turn(self):
        return self.order.turn

    @property
    def is_hold(self):
        return self.type == CommandType.HOLD

    @property
    def is_move(self):
        return self.type == CommandType.MOVE

    @property
    def is_support(self):
        return self.type == CommandType.SUPPORT

    @property
    def is_convoy(self):
        return self.type == CommandType.CONVOY

    # TODO move this to decisions
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
        if self.source.piece.is_fleet:
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
        if self.source.piece.is_army:
            if self.source.coastal and self.target.coastal:
                return self.successful_convoy_exists
        return False

    # TODO move this to decisions (becuase relates only to move path)
    @property
    def successful_convoy_exists(self):
        """
        Determine whether a successful convoy exists between ``source`` and
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

        if not self.target.piece.command.is_move:
            return False

        # if the target piece is moving to this space and has path
        if self.target.piece.command.target == self.source:
            if self.target.piece.command.move_path:
                if not self.target.piece.command.via_convoy and not self.via_convoy:
                    return True
        return False

    # move to manager?
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
