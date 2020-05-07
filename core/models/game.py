import random

from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django.db.models.manager import Manager

from core.models.base import NationChoiceMode, GameStatus, DeadlineFrequency


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


class Game(models.Model):

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
    # TODO needs to use a through model so we can record: joined at, etc.
    participants = models.ManyToManyField(
        User,
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

    objects = GameManager()

    class Meta:
        db_table = "game"

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
        return self.participants.count() == self.num_players \
            and not self.turns.all().exists()

    def initialize(self):
        """
        When all players have joined a game, the game is initialized.
        """
        # Assign players to nation randomly
        # Create pieces
        # Create piece states
        # Create nation states
        # Create territory states
        pass

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
        turn_model.objects.create_turn_from_previous_turn(current_turn)
