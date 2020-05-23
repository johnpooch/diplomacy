from django.db import models

from core.models.base import TerritoryDisplayType


class MapData(models.Model):
    variant = models.ForeignKey(
        'Variant',
        on_delete=models.CASCADE,
        related_name='map_data',
    )
    identifier = models.CharField(
        max_length=200,
        null=False,
    )
    width = models.FloatField()
    height = models.FloatField()


class TerritoryMapData(models.Model):
    """
    How a territory should be displayed on the map.
    """
    map_data = models.ForeignKey(
        'MapData',
        on_delete=models.CASCADE,
        related_name='territory_data',
    )
    # impassable territories like Switzerland do not specify a territory.
    territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        null=True,
        related_name='map_data',
    )
    type = models.CharField(
        max_length=100,
        null=False,
        choices=TerritoryDisplayType.CHOICES,
    )
    name = models.CharField(
        max_length=100,
        null=True,
    )
    abbreviation = models.CharField(
        max_length=100,
        null=True,
    )
    path = models.TextField(
        null=False,
    )
    text_x = models.FloatField(
        null=True
    )
    text_y = models.FloatField(
        null=True
    )
    piece_x = models.FloatField(
        null=True
    )
    piece_y = models.FloatField(
        null=True
    )
    dislodged_piece_x = models.FloatField(
        null=True
    )
    dislodged_piece_y = models.FloatField(
        null=True
    )
    supply_center_x = models.FloatField(
        null=True
    )
    supply_center_y = models.FloatField(
        null=True
    )


class NamedCoastMapData(models.Model):
    """
    How pieces on a named coast should be displayed on the map.
    """
    map_data = models.ForeignKey(
        'MapData',
        on_delete=models.CASCADE,
        related_name='named_coast_data',
    )
    named_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        null=False,
        related_name='map_data',
    )
    name = models.CharField(
        max_length=100,
        null=False,
    )
    abbreviation = models.CharField(
        max_length=100,
        null=False,
    )
    text_x = models.FloatField(
        null=True
    )
    text_y = models.FloatField(
        null=True
    )
    piece_x = models.FloatField(
        null=True
    )
    piece_y = models.FloatField(
        null=True
    )
    dislodged_piece_x = models.FloatField(
        null=True
    )
    dislodged_piece_y = models.FloatField(
        null=True
    )
