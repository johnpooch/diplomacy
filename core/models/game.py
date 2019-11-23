from django.contrib.auth.models import User
from django.db import models

from core.models.base import GameStatus


class Game(models.Model):
    """
    """
    name = models.CharField(
        max_length=50,
        null=False
    )
    status = models.CharField(
        max_length=22,
        choices=GameStatus.CHOICES,
        default=GameStatus.AWAITING_PARTICIPANTS,
        null=False,
    )
    participants = models.ManyToManyField(
        User,
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
