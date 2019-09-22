from django.db import models


class Phase(models.Model):
    """
    """
    SEASONS = (
        ('S', 'Spring'),
        ('F', 'Fall'),
    )
    PHASE_TYPES = (
        ('O', 'Order'),
        ('R', 'Retreat and Disband'),
        ('B', 'Build and Disband'),
    )
    season = models.CharField(max_length=1, choices=SEASONS, null=False)
    type = models.CharField(max_length=1, choices=PHASE_TYPES, null=False)

    class Meta:
        db_table = "phase"

    def __str__(self):
        return " ".join([self.get_type_display(), self.get_season_display()])
