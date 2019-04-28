from django.db import models


class Nation(models.Model):
    """
    """
    name = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name


class Piece(models.Model):
    """
    """
    PIECE_TYPES = (
        ('A', 'Army'),
        ('F', 'Fleet'),
    )
    
    nation = models.ForeignKey('Nation', related_name='pieces',
            on_delete=models.CASCADE, db_column="nation_id", null=False,
            db_constraint=False)
    type = models.CharField(max_length=1, choices=PIECE_TYPES, null=False)
    territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            db_column='territory_id', null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return ' '.join([self.get_type_display(), self.territory.display_name])


class SupplyCenter(models.Model):
    """
    """
    owner = models.ForeignKey('Nation', related_name='supply_centers',
            on_delete=models.CASCADE, db_column='nation_id', null=True)
    territory = models.ForeignKey('Territory', related_name='supply_center',
            on_delete=models.CASCADE, db_column='territory_id', null=False)

    def __str__(self):
        return self.territory.display_name

class Territory(models.Model):
    """
    """

    TERRITORY_TYPES = (
        ('L', 'Land'),
        ('S', 'Sea'),
    )

    abbreviation = models.CharField(max_length=6, null=False)
    display_name = models.CharField(max_length=50, null=False)
    nationity = models.ForeignKey('Nation', on_delete=models.CASCADE,
            db_column='nation_id', null=True)
    neighours = models.ManyToManyField('self', related_name='neighbours',
            blank=True)
    shared_coasts = models.ManyToManyField('self', related_name='shared_coasts',
            blank=True)
    type = models.CharField(max_length=10, choices=TERRITORY_TYPES, null=False)
    coast = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name
 
