from django.contrib.auth.models import User
from django.db import models
from django.db.models.manager import BaseManager

from core.models.base import NationChoiceMode, GameStatus, DeadlineFrequency


class GameQuerySet(models.QuerySet):
    """
    """

    def filter_by_joinable(self, user=None):
        """
        Filters games which are joinable, i.e. have fewer participants than
        num_players and are not ended.

        Args:
            * ``[user]`` - If provided, games in which the given user is
            participating are excluded.
        """
        if user:
            self = self.exclude(participants=user)
        return self \
            .annotate(participant_count=models.Count('participants'))\
            .filter(participant_count__lt=models.F('num_players'))\
            .exclude(status=GameStatus.ENDED)


class GameManager(BaseManager.from_queryset(GameQuerySet)):
    pass


class Game(models.Model):
    """
    """
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
        max_length=100,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=22,
        choices=GameStatus.CHOICES,
        default=GameStatus.PENDING,
        null=False,
    )
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

    def get_current_turn(self):
        """
        Gets the related ``Turn`` where ``current_turn`` is ``True``.

        Returns:
            * ``Turn``
        """
        return self.turns.get(current_turn=True)
