from django.db import models


class Game(models.Model):
    """
    """
    name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "game"

    def get_current_turn(self):
        """
        Gets the related ``Turn`` where ``current_turn`` is ``True``.

        Returns:
            * ``Turn``
        """
        return self.turns.get(current_turn=True)
