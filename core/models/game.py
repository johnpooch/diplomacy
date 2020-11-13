import random

from django.apps import apps
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
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
        'NationState',
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
        null=False,
        choices=DeadlineFrequency.CHOICES,
        default=DeadlineFrequency.TWENTY_FOUR_HOURS,
        max_length=100,
    )
    retreat_deadline = models.CharField(
        null=False,
        choices=DeadlineFrequency.CHOICES,
        default=DeadlineFrequency.TWENTY_FOUR_HOURS,
        max_length=100,
    )
    build_deadline = models.CharField(
        null=False,
        choices=DeadlineFrequency.CHOICES,
        default=DeadlineFrequency.TWELVE_HOURS,
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
        return turn_model.objects.create(
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
        return self.turns.get(current_turn=True)

    def process(self):
        current_turn = self.get_current_turn()
        current_turn.process()
        turn_model = apps.get_model('core', 'Turn')
        new_turn = turn_model.objects.create_turn_from_previous_turn(
            current_turn
        )
        # check win conditions
        winning_nation = new_turn.check_for_winning_nation()
        if winning_nation:
            self.set_winner(winning_nation)

    def set_winner(self, nation_state):
        """
        End the game and set the winning nation.
        """
        self.status = GameStatus.ENDED
        self.save()
        self.winners.add(nation_state)
