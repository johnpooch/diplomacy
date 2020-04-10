from django.db import models
from core.models.base import Phase, Season


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
