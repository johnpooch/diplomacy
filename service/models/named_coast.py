from django.db import models


class NamedCoast(models.Model):
    """
    A territory can have multiple named coasts.

    A named coast has neighbours which is a sub set of the parent territory's
    neighbours.

    The related name of the named coasts to the neighbouring territories is
    ``named_coast_neighbours``.

    A named coast can only be occupied by a fleet. A fleet cannot enter a
    territory with named coasts without also occupying a named coast.

    When a fleet is occupying a named coast it is also occupying the parent
    territory. This takes effect when resolving challenges and also when
    resolving supply center control.

    A fleet can only from a named coast to a territory which is a neighbour of
    the named coast and vice versa.

    The parent territory is still considered a coastal territory.
    """
    name = models.CharField(max_length=100, null=False)
    map_abbreviation = models.CharField(max_length=50, null=False)
    parent = models.ForeignKey(
        'Territory',
        null=False,
        on_delete=models.CASCADE,
        related_name='named_coasts',
    )
    neighbours = models.ManyToManyField(
        'Territory',
        symmetrical=True,
        blank=True,
        related_name='named_coast_neighbours',
    )
