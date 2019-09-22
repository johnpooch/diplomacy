from django.db import models


class Nation(models.Model):
    # TODO should make some sort of PerGame base model.
    """
    """
    # TODO nation should have a color field
    name = models.CharField(max_length=15)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "nation"

    def has_pieces_which_must_retreat(self):
        return any([piece.must_retreat for piece in self.pieces.all()])

    def __str__(self):
        return self.name
