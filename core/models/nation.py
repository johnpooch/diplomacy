from django.db import models


class Nation(models.Model):
    # TODO should make some sort of PerGame base model.
    """
    """
    name = models.CharField(max_length=15)
    active = models.BooleanField(default=True)
    # TODO should have a foreign key to variant

    class Meta:
        db_table = "nation"

    def has_pieces_which_must_retreat(self):
        return any([piece.must_retreat for piece in self.pieces.all()])

    def __str__(self):
        return self.name


class NationState(models.Model):
    """
    Through model between ``Game``, ``User``, and ``Nation``. Represents the
    state of a nation in a game.
    """
    turn = models.ForeignKey(
        'Turn',
        null=False,
        related_name='nation_states',
        on_delete=models.CASCADE,
    )
    nation = models.ForeignKey(
        'Nation',
        null=False,
        related_name='+',
        on_delete=models.CASCADE,
    )

    # player = models.ForeignKey(
    #     '',
    #     null=True,
    #     related_name='+',
    #     on_delete=models.CASCADE,
    # )

    surrendered = models.BooleanField(
        null=True,
        default=False,
    )
    surrendered_turn = models.ForeignKey(
        'Turn',
        null=True,
        related_name='+',
        on_delete=models.CASCADE,
    )
