from django.contrib.auth.models import User
from django.db import models

from core.models.base import CountryChoiceMode, GameStatus, DeadlineFrequency


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
    country_choice_mode = models.CharField(
        null=False,
        choices=CountryChoiceMode.CHOICES,
        default=CountryChoiceMode.RANDOM,
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

    class Meta:
        db_table = "game"

    def get_current_turn(self):
        """
        Gets the related ``Turn`` where ``current_turn`` is ``True``.

        Returns:
            * ``Turn``
        """
        return self.turns.get(current_turn=True)
