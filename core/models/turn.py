from django.db import models


class Turn(models.Model):
    """
    """
    year = models.IntegerField()
    phase = models.ForeignKey('Phase', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)
    current_turn = models.BooleanField(default=True)

    class Meta:
        db_table = "turn"

    def __str__(self):
        return " ".join([str(self.phase), str(self.year)])
