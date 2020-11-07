from django.apps import apps
from django.db import IntegrityError, models
from django.utils import timezone

from adjudicator import process_game_state

from core.models.base import OrderType, OutcomeType, Phase, Season, TerritoryType


possible_orders = {
    Phase.ORDER: [
        OrderType.MOVE,
        OrderType.CONVOY,
        OrderType.HOLD,
        OrderType.SUPPORT
    ],
    Phase.RETREAT_AND_DISBAND: [
        OrderType.RETREAT,
        OrderType.DISBAND
    ],
    Phase.BUILD: [
        OrderType.BUILD,
        OrderType.DISBAND
    ],
}


class TurnManager(models.Manager):

    # TODO move this method outside manager
    def create_turn_from_previous_turn(self, previous_turn):
        # NOTE how about we make the turn have 0 year until finished
        piece_state_model = apps.get_model('core', 'PieceState')
        new_turn = Turn.objects.create(
            game=previous_turn.game,
            year=0,
            season=Season.SPRING,
            phase=Phase.ORDER,
            current_turn=True,
        )

        # get successful move orders
        successful_move_orders = previous_turn.orders.filter(
            outcome=OutcomeType.SUCCEEDS,
            type=OrderType.MOVE,
        )
        # get successful retreat orders
        successful_retreat_orders = previous_turn.orders.filter(
            outcome=OutcomeType.SUCCEEDS,
            type=OrderType.RETREAT,
        )

        for piece_state in previous_turn.piecestates.all():
            # If piece disbanded do not create a new piece state
            if piece_state.piece.turn_disbanded:
                continue
            piece_data = {
                'piece': piece_state.piece,
                'turn': new_turn,
                'territory': piece_state.territory,
                'named_coast': piece_state.named_coast,
            }
            for order in successful_move_orders:
                if piece_state.territory == order.source:
                    piece_data['territory'] = order.target
                    piece_data['named_coast'] = order.target_coast

            for order in successful_retreat_orders:
                if piece_state.territory == order.source and piece_state.must_retreat:
                    piece_data['territory'] = order.target

            # if piece dislodged set next piece to must_retreat
            if piece_state.dislodged:
                piece_data['must_retreat'] = True

            piece_state_model.objects.create(**piece_data)
        for territory_state in previous_turn.territorystates.all():
            territory_state.turn = new_turn
            territory_state.pk = None
            # if end of fall orders process change of possession.
            if previous_turn.phase == Phase.ORDER \
                    and previous_turn.season == Season.FALL \
                    and not territory_state.territory.type == TerritoryType.SEA:
                try:
                    occupying_piece = new_turn.piecestates.get(
                        territory=territory_state.territory,
                        must_retreat=False
                    )
                    territory_state.controlled_by = occupying_piece.piece.nation
                except piece_state_model.DoesNotExist:
                    pass

            territory_state.contested = territory_state.bounce_occurred
            territory_state.bounce_occurred = False

            territory_state.save()
        for nation_state in previous_turn.nationstates.all():
            # TODO account for nations which have been eliminated?
            nation_state.turn = new_turn
            nation_state.orders_finalized = False
            nation_state.pk = None
            nation_state.save()
        new_turn.season, new_turn.phase, new_turn.year = \
            previous_turn.get_next_season_phase_and_year(new_turn)
        new_turn.save()

        return new_turn


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

    def process(self):
        game_state_dict = self._to_game_state_dict()
        outcome = process_game_state(game_state_dict)
        self.update_turn(outcome)

    def update_turn(self, outcome):
        piece_state_model = apps.get_model('core', 'PieceState')
        piece_model = apps.get_model('core', 'Piece')
        self.processed = True
        self.processed_at = timezone.now()
        self.save()
        if self.phase in [Phase.RETREAT_AND_DISBAND, Phase.BUILD]:
            for order_data in outcome['orders']:
                order = self.orders.get(id=order_data['id'])
                if order.type == OrderType.DISBAND:
                    if self.phase == Phase.RETREAT_AND_DISBAND:
                        piece = order.source.pieces.get(
                            turn=self,
                            must_retreat=True
                        ).piece
                    else:
                        piece = order.source.pieces.get(turn=self).piece
                    piece.turn_disbanded = self
                    piece.save()
                if order.type == OrderType.BUILD and \
                        order_data['outcome'] == OutcomeType.SUCCEEDS:
                    piece = piece_model.objects.create(
                        game=self.game,
                        turn_created=self,
                        nation=order.nation,
                        type=order.piece_type,
                    )
                    piece_state_model.objects.create(
                        turn=self,
                        piece=piece,
                        territory=order.source,
                        named_coast=order.target_coast,
                    )
        for territory_data in outcome.get('territories', []):
            territory_state = self.territorystates.get(territory__id=territory_data['id'])
            territory = territory_state
            territory.bounce_occurred = territory_data['bounce_occurred']
            territory.save()
        for order_data in outcome['orders']:
            order = self.orders.get(id=order_data['id'])
            order.outcome = order_data.get('outcome')
            order.outcome_verbose = order_data.get('outcome_verbose')
            order.legal = bool(not order_data['illegal'])
            order.illegal_verbose = order_data['illegal_verbose']
            order.save()
        for piece_data in outcome.get('pieces', []):
            piece = self.piecestates.get(id=piece_data['id'])
            dislodged = piece_data['dislodged_decision'] == 'dislodged'
            piece.dislodged = dislodged
            if dislodged:
                _id = piece_data['dislodged_by']
                piece.dislodged_by = self.piecestates.get(id=_id)
            attacker_territory = piece_data['attacker_territory']
            if attacker_territory:
                territory_model = apps.get_model('core', 'Territory')
                _id = attacker_territory
                piece.attacker_territory = territory_model.objects.get(id=_id)
            piece.destroyed = piece_data['destroyed']
            piece.destroyed_message = piece_data['destroyed_message']
            if piece.destroyed:
                piece.piece.turn_disbanded = self
                piece.piece.save()
            piece.save()

    def _to_game_state_dict(self):
        """
        Convert the turn and all related objects into a single game state dict
        to be process by the adjudicator.

        Returns:
            * `dict`
        """
        game_state = dict()
        territory_states = self.territorystates.all()
        piece_states = self.piecestates.all()
        orders = self.orders.all()
        game_state['territories'] = [t.to_dict() for t in territory_states]
        game_state['pieces'] = [p.to_dict() for p in piece_states]
        game_state['orders'] = [o.to_dict() for o in orders]
        # un nest named_coasts
        game_state['named_coasts'] = list()
        for t in game_state['territories']:
            named_coasts = t.pop('named_coasts')
            for n in named_coasts:
                game_state['named_coasts'].append(n)
        game_state['phase'] = self.phase
        game_state['variant'] = self.game.variant.name
        return game_state

    def get_next_season_phase_and_year(self, new_turn):
        if not self.processed:
            raise ValueError('Cannot get next phase until order is processed.')

        if self.piecestates.filter(dislodged=True).exists():
            return self.season, Phase.RETREAT_AND_DISBAND, self.year

        if self.season == Season.SPRING:
            return Season.FALL, Phase.ORDER, self.year

        if self.season == Season.FALL and not self.phase == Phase.BUILD:
            for nation_state in new_turn.nationstates.all():
                if abs(nation_state.supply_delta):
                    return self.season, Phase.BUILD, self.year
        return Season.SPRING, Phase.ORDER, self.year + 1


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
            * `datetime` - `datetime` - When article is to be published. If
            datetime is not in the future, the minimum value of timezone.now()
            is used.
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
        related_name='end',
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
