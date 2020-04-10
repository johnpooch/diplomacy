from django.db import models


class NamedCoast(models.Model):

    name = models.CharField(
        max_length=100,
        null=False
    )
    map_abbreviation = models.CharField(
        max_length=50,
        null=False
    )
    parent = models.ForeignKey(
        'Territory',
        null=False,
        on_delete=models.CASCADE,
        related_name='named_coasts',
    )
    neighbours = models.ManyToManyField(
        'Territory',
        blank=True,
        related_name='named_coast_neighbours',
    )

    class Meta:
        db_table = 'named_coast'
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'map_abbreviation'],
                name='unique_coast_abbreviation'
            ),
            models.UniqueConstraint(
                fields=['parent', 'name'],
                name='unique_coast_name'
            )
        ]
