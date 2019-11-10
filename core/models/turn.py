from django.db import models
from core.models.base import Phase, Season


class Turn(models.Model):
    """
    """
    game = models.ForeignKey(
        'Game',
        on_delete=models.CASCADE,
        null=False,
        related_name='turns',
    )
    season = models.CharField(max_length=7, choices=Season.CHOICES, null=False)
    phase = models.CharField(max_length=20, choices=Phase.CHOICES, null=False)
    year = models.IntegerField()
    current_turn = models.BooleanField(default=True)

    class Meta:
        db_table = "turn"

    def __str__(self):
        return " ".join([
            self.get_season_display(),
            str(self.year),
            self.get_phase_display(),
            'Phase'
        ])

    def pieces(self):
        pass
