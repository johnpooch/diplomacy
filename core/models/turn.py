from django.apps import apps
from django.db import models
from django.utils import timezone

from adjudicator import process_game_state

from core.models.base import OrderType, OutcomeType, Phase, Season


possible_orders = {
    Phase.ORDER: [OrderType.MOVE, OrderType.CONVOY, OrderType.HOLD, OrderType.SUPPORT],
    Phase.RETREAT_AND_DISBAND: [OrderType.RETREAT, OrderType.DISBAND],
    Phase.BUILD: [OrderType.BUILD, OrderType.DISBAND],
}


class TurnManager(models.Manager):

    def create_turn_from_previous_turn(self, previous_turn):
        season, phase, year = previous_turn.get_next_season_phase_and_year()
        new_turn = Turn.objects.create(
            game=previous_turn.game,
            year=year,
            season=season,
            phase=phase,
            current_turn=True,
        )

        # get successful move orders
        successful_move_orders = previous_turn.orders.filter(
            outcome=OutcomeType.MOVES,
            type=OrderType.MOVE,
        )
        for piece_state in previous_turn.piecestates.all():
            piece_data = {
                'piece': piece_state.piece,
                'turn': new_turn,
                'territory': piece_state.territory,
            }
            for order in successful_move_orders:
                if piece_state.territory == order.source:
                    piece_data['territory'] = order.target

            piece_state_model = apps.get_model('core', 'PieceState')
            piece_state_model.objects.create(**piece_data)
        for territory_state in previous_turn.territorystates.all():
            # If end of fall orders process change of possession.
            territory_state.turn = new_turn
            territory_state.pk = None
            territory_state.save()
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

    @property
    def possible_order_types(self):
        return possible_orders[self.phase]

    @property
    def ready_to_process(self):
        return not self.nationstates.filter(orders_finalized=False).exists()

    def process(self):
        game_state_dict = self._to_game_state_dict()
        outcome = process_game_state(game_state_dict)
        self.update_turn(outcome)

    def update_turn(self, outcome):
        self.processed = True
        self.processed_at = timezone.now()
        self.save()
        for territory_data in outcome['territories']:
            territory_state = self.territorystates.get(territory__id=territory_data['id'])
            territory = territory_state
            territory.contested = territory_data['contested']
            territory.save()
        for order_data in outcome['orders']:
            order = self.orders.get(id=order_data['id'])
            order.outcome = order_data.get('outcome')
            order.legal = order_data['legal_decision'] == 'legal'
            order.illegal_message = order_data['illegal_message']
            order.save()
        for piece_data in outcome['pieces']:
            piece = self.piecestates.get(id=piece_data['id'])
            piece.dislodged = piece_data['dislodged_decision'] == 'dislodged'
            piece.dislodged_by = piece_data['dislodged_by']
            piece.attacker_territory = piece_data['attacker_territory']
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

    def get_next_season_phase_and_year(self):
        # TODO finish and test
        if not self.processed:
            raise ValueError('Cannot get next phase until order is processed.')

        if self.piecestates.filter(dislodged=True).exists():
            return self.season, Phase.RETREAT_AND_DISBAND, self.year

        if self.season == Season.SPRING:
            return Season.FALL, Phase.ORDER, self.year

        if self.season == Season.FALL:
            # if any change in supply center control
            if False:
                return self.season, Phase.BUILD, self.year
            return Season.SPRING, Phase.ORDER, self.year + 1


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
