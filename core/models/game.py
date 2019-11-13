from django.contrib.auth.models import User
from django.db import models


class Game(models.Model):
    """
    """
    # TODO add game state, e.g. pending, live, finished
    name = models.CharField(
        max_length=50,
        null=False
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
