import random
from copy import copy

from django.apps import apps
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models.manager import Manager
from django.utils import timezone

from core.models.base import DeadlineFrequency, GameStatus, NationChoiceMode
from core.models.mixins import AutoSlug


class GameQuerySet(models.QuerySet):

    def filter_by_joinable(self, user=None):
        """
        Filters games which are joinable, i.e. have fewer participants than
        num_players and are not ended.

        Args:
            * `[user]` - If provided, games in which the given user is
            participating are excluded.
        """
        qs = self
        if user:
            qs = self.exclude(participants=user)
        return qs \
            .annotate(participant_count=models.Count('participants'))\
            .filter(participant_count__lt=models.F('num_players'))\
            .exclude(status=GameStatus.ENDED)


class GameManager(Manager.from_queryset(GameQuerySet)):
    pass


class Game(models.Model, AutoSlug):

    variant = models.ForeignKey(
        'Variant',
        null=False,
        on_delete=models.CASCADE,
        related_name='games',
    )
    name = models.CharField(
        max_length=50,
        null=False
    )
    slug = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        db_index=True,
        unique=True,
    )
    description = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=22,
        choices=GameStatus.CHOICES,
        default=GameStatus.PENDING,
        null=False,
        editable=False,
    )
    participants = models.ManyToManyField(
        User,
        through='Participation',
    )
    winners = models.ManyToManyField(
        'Nation',
    )
    private = models.BooleanField(
        default=False,
    )
    password = models.CharField(
        null=True,
        blank=True,
        max_length=100,
    )
    order_deadline = models.CharField(
        null=True,
        choices=DeadlineFrequency.CHOICES,
        max_length=100,
    )
    retreat_deadline = models.CharField(
        null=True,
        choices=DeadlineFrequency.CHOICES,
        max_length=100,
    )
    build_deadline = models.CharField(
        null=True,
        choices=DeadlineFrequency.CHOICES,
        max_length=100,
    )
    process_on_finalized_orders = models.BooleanField(
        default=True,
    )
    nation_choice_mode = models.CharField(
        null=False,
        choices=NationChoiceMode.CHOICES,
        default=NationChoiceMode.RANDOM,
        max_length=100,
    )
    num_players = models.PositiveIntegerField(
        null=False,
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='created_games',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    initialized_at = models.DateTimeField(
        null=True,
    )

    objects = GameManager()

    def __str__(self):
        return self.name

    @property
    def ended(self):
        """
        Shortcut to determine whether the game has ended.

        Returns:
            * `bool`
        """
        # TODO test
        return self.status == GameStatus.ENDED

    @property
    def joinable(self):
        """
        A game is joinable when the number of participants is fewer than the
        `num_players` value.

        Returns:
            * `bool`
        """
        # TODO test
        return self.participants.count() < self.num_players and not self.ended

    @property
    def ready_to_initialize(self):
        """
        True when the correct number of players have joined and the game hasn't
        been initialized.
        """
        return self.participants.all().count() >= self.num_players \
            and not self.turns.all().exists()

    def initialize(self):
        """
        When all players have joined a game, the game is initialized.
        """
        self.create_initial_turn()
        self.create_initial_nation_states()
        self.create_initial_territory_states()
        self.create_initial_pieces()
        self.status = GameStatus.ACTIVE
        self.initialized_at = timezone.now()
        self.save()

    def create_initial_turn(self):
        """
        Creates the first turn of the game.

        Returns:
            * `Turn`
        """
        variant = self.variant
        turn_model = apps.get_model('core', 'Turn')
        return turn_model.objects.new(
            game=self,
            year=variant.starting_year,
            season=variant.starting_season,
            phase=variant.starting_phase,
            current_turn=True,
        )

    def create_initial_nation_states(self):
        """
        Creates the initial nation states and assigns each participant to a
        nation state randomly.
        """
        participants = list(self.participants.all())
        nations = list(self.variant.nations.all())
        random.shuffle(participants)
        nation_state = apps.get_model('core', 'NationState')
        for participant, nation in zip(participants, nations):
            nation_state.objects.create(
                turn=self.get_current_turn(),
                nation=nation,
                user=participant,
            )

    def create_initial_territory_states(self):
        """
        Creates the initial territory states.
        """
        territories = list(self.variant.territories.all())
        territory_state = apps.get_model('core', 'TerritoryState')
        for territory in territories:
            territory_state.objects.create(
                turn=self.get_current_turn(),
                territory=territory,
                controlled_by=territory.controlled_by_initial,
            )

    def create_initial_pieces(self):
        """
        Create a piece on every territory that has a starting piece.
        """
        territories = list(self.variant.territories.all())
        piece_model = apps.get_model('core', 'Piece')
        piece_state_model = apps.get_model('core', 'PieceState')
        for territory in territories:
            if territory.initial_piece_type:
                piece = piece_model.objects.create(
                    game=self,
                    type=territory.initial_piece_type,
                    nation=territory.controlled_by_initial,
                )
                piece_state = piece_state_model.objects.create(
                    turn=self.get_current_turn(),
                    piece=piece,
                    territory=territory,
                )
                try:
                    starting_coast = territory.named_coasts.get(
                        piece_starts_here=True
                    )
                    piece_state.named_coast = starting_coast
                    piece_state.save()
                except ObjectDoesNotExist:
                    pass

    def get_current_turn(self):
        """
        Gets the related `Turn` where `current_turn` is `True`.

        Returns:
            * `Turn`
        """
        return next(
            iter(t for t in self.turns.all() if t.current_turn),
            None
        )

    def set_winners(self, *nations):
        """
        End the game and set the winning nation(s).

        Args:
            * `nations` - one or more `Nation` instances.
        """
        for nation in nations:
            if nation.variant != self.variant:
                raise ValueError(
                    'Nation does not belong to the same variant as this game'
                )
        self.status = GameStatus.ENDED
        self.save()
        self.winners.set(nations)

    @transaction.atomic
    def restore_turn(self, turn):
        """
        Create a copy of the given turn and set it to be the current turn. Archive
        the original turn and all later turns in this game.

        Args:
            *  `turn` - `Turn` -The turn to restore to.

        Returns:
            *  `Turn` - The restored turn
        """
        if self.status != GameStatus.ACTIVE:
            raise ValueError('Cannot restore turn on inactive game')
        if turn.game.id != self.id:
            raise ValueError('Cannot restore to turn of other game')
        if turn.current_turn:
            raise ValueError('Cannot restore to current turn')

        # Archive turns
        self.turns \
            .filter(archived=False, id__gte=turn.id) \
            .update(archived=True, current_turn=False)

        # Create new turn
        restored_turn = copy(turn)
        restored_turn.pk = None
        restored_turn.id = None
        restored_turn.current_turn = True
        restored_turn.processed = False
        restored_turn.processed_at = None
        restored_turn.next_season = None
        restored_turn.next_phase = None
        restored_turn.next_year = None
        restored_turn.archived = False
        restored_turn.restored_from = turn
        restored_turn.save()

        # Copy over piece states
        for piece_state in turn.piecestates.all():
            piece_state.restore_to_turn(restored_turn)

        # Copy over territory states
        for territory_state in turn.territorystates.all():
            territory_state.restore_to_turn(restored_turn)

        # Copy over nation states
        for nation_state in turn.nationstates.all():
            nation_state.restore_to_turn(restored_turn)

        return restored_turn
