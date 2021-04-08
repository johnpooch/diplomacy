from django.db import IntegrityError, models
from django.utils import timezone

from core.models.base import OrderType, Phase, Season
from core.utils.date import timespan


possible_orders = {
    Phase.ORDER: [
        OrderType.MOVE,
        OrderType.CONVOY,
        OrderType.HOLD,
        OrderType.SUPPORT
    ],
    Phase.RETREAT: [
        OrderType.RETREAT,
        OrderType.DISBAND
    ],
    Phase.BUILD: [
        OrderType.BUILD,
        OrderType.DISBAND
    ],
}


class TurnManager(models.Manager):

    def new(self, **kwargs):
        """
        Create a new `Turn` instance and also create a related `TurnEnd`
        instance.
        """
        turn = self.create(**kwargs)
        td = timespan.get_timespan(turn.deadline).timedelta
        turn_end_dt = timezone.now() + td
        TurnEnd.objects.new(turn, turn_end_dt)
        return turn


class Turn(models.Model):

    game = models.ForeignKey(
        'Game',
        on_delete=models.CASCADE,
        null=False,
        related_name='turns',
    )
    season = models.CharField(
        max_length=7,
        choices=Season.CHOICES,
        null=False,
    )
    phase = models.CharField(
        max_length=20,
        choices=Phase.CHOICES,
        null=False,
    )
    year = models.PositiveIntegerField(
        null=False,
    )
    next_season = models.CharField(
        max_length=7,
        choices=Season.CHOICES,
        null=True,
    )
    next_phase = models.CharField(
        max_length=20,
        choices=Phase.CHOICES,
        null=True,
    )
    next_year = models.PositiveIntegerField(
        null=True,
    )
    current_turn = models.BooleanField(
        default=True,
    )
    processed = models.BooleanField(
        default=False,
    )
    processed_at = models.DateTimeField(
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    objects = TurnManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'year', 'season', 'phase'],
                name='unique_phase_per_game,'
            )
        ]

    def __str__(self):
        return " ".join([
            f'[{self.game.name}]',
            self.get_season_display(),
            str(self.year),
            self.get_phase_display(),
            'Phase'
        ])

    @classmethod
    def get_next(cls, turn):
        try:
            return cls.objects.filter(game=turn.game, id__gt=turn.id) \
                .order_by('id')[0]
        except IndexError:
            return None

    @classmethod
    def get_previous(cls, turn):
        try:
            return cls.objects.filter(game=turn.game, id__lt=turn.id) \
                .order_by('-id')[0]
        except IndexError:
            return None

    @property
    def possible_order_types(self):
        return possible_orders[self.phase]

    @property
    def public_orders(self):
        if self.current_turn:
            return self.orders.none()
        return self.orders.all()

    @property
    def ready_to_process(self):
        """
        Determine whether all nations which need to finalize their orders have
        finalized.

        Returns:
            * `bool`
        """
        for ns in self.nationstates.all():
            if not ns.orders_finalized:
                if self.phase == Phase.BUILD:
                    if (ns.num_builds or ns.num_disbands):
                        return False
                else:
                    if ns.pieces_to_order:
                        return False
        return True

    @property
    def turn_end(self):
        try:
            return self.turnend
        except TurnEnd.DoesNotExist:
            return None

    @property
    def deadline(self):
        if self.phase == Phase.ORDER:
            return self.game.order_deadline
        if self.phase == Phase.RETREAT:
            return self.game.retreat_deadline
        if self.phase == Phase.BUILD:
            return self.game.build_deadline

    def check_for_winning_nation(self):
        """
        Iterate through every nation and check if any nation satisfies the
        victory conditions of the game variant.

        Returns:
            * `NationState` or `None`
        """
        # TODO filter by active/not surrendered
        for nation_state in self.nationstates.all():
            if nation_state.meets_victory_conditions:
                return nation_state
        return None

    def _ensure_current_turn(self):
        if not self.current_turn:
            raise ValueError('This is not the current turn of the game.')


class TurnEndManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().order_by('datetime')

    def new(self, turn, datetime):
        """
        Create a task to process a turn.

        This method will set up an async task to run process_turn() at the
        date given, and return the created TurnEnd object to represent
        this task.

        Args:
            * `turn` - `Turn` - Turn to be processed.
            * `datetime` - `datetime` - When the turn is to be processed.
        """
        from ..tasks import process_turn

        if turn.turn_end:
            raise IntegrityError(
                'A TurnEnd for turn ID %d already exists.' % turn.id
            )

        task = process_turn.apply_async(
            kwargs={
                'turn_id': turn.id,
                'processed_at': datetime,
            },
            eta=datetime,
        )

        return self.create(turn=turn, datetime=datetime, task_id=task.id)


class TurnEnd(models.Model):
    """
    Represents the future end of a turn.

    When created properly (using `TurnEnd.objects.new`), this model will
    automatically be associated with an `AsyncResult` object for the
    `upcoming process_turn()` task.
    """
    turn = models.OneToOneField(
        'Turn',
        null=False,
        on_delete=models.CASCADE,
    )
    datetime = models.DateTimeField(
        null=False,
    )
    task_id = models.CharField(
        max_length=255,
        null=True,
    )

    objects = TurnEndManager()
