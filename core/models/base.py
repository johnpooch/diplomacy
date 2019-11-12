from django.core.exceptions import ValidationError
from django.db import models


class PieceType:
    ARMY = 'army'
    FLEET = 'fleet'
    CHOICES = (
        (ARMY, 'Army'),
        (FLEET, 'Fleet'),
    )


class CommandType:
    HOLD = 'hold'
    MOVE = 'move'
    SUPPORT = 'support'
    CONVOY = 'convoy'
    RETREAT = 'retreat'
    BUILD = 'build'
    DISBAND = 'disband'
    CHOICES = (
        (HOLD, 'Hold'),
        (MOVE, 'Move'),
        (SUPPORT, 'Support'),
        (CONVOY, 'Convoy'),
        (RETREAT, 'Retreat'),
        (BUILD, 'Build'),
        (DISBAND, 'Disband')
    )


class CommandState:
    UNRESOLVED = 'unresolved'
    SUCCEEDS = 'succeeds'
    FAILS = 'fails'
    CHOICES = (
        (UNRESOLVED, 'Unresolved'),
        (SUCCEEDS, 'Succeeds'),
        (FAILS, 'Fails')
    )


class DislodgedState:
    UNRESOLVED = 'unresolved'
    SUSTAINS = 'sustains'
    DISLODGED = 'dislodged'
    CHOICES = (
        (UNRESOLVED, 'Unresolved'),
        (SUSTAINS, 'Sustains'),
        (DISLODGED, 'Dislodged')
    )


class TerritoryType:
    LAND = 'land'
    SEA = 'sea'
    CHOICES = (
        (LAND, 'Land'),
        (SEA, 'Sea'),
    )


class Phase:
    ORDER = 'order'
    RETREAT_AND_DISBAND = 'retreat and disband'
    BUILD = 'build'
    CHOICES = (
        (ORDER, 'Order'),
        (RETREAT_AND_DISBAND, 'Retreat and Disband'),
        (BUILD, 'Build')
    )


class Season:
    FALL = 'fall'
    SPRING = 'spring'
    CHOICES = (
        (FALL, 'Fall'),
        (SPRING, 'Spring'),
    )


class HygenicModel(models.Model):
    """
    Models which inherit from this base will run ``Model.full_clean()`` before
    save (on pre_save signal). Any ``ValidationError`` raised during this
    operation will be re-raised as a ``ValueError``, causing the save operation
    to fail.

    This class relies upon the ``hygenic_model_pre_save()`` function
    in ``core.signals`` module to work properly.
    """
    class Meta:
        abstract = True

    def pre_save_clean(self, sender, **kwargs):
        """
        Run ``full_clean()`` and raise any validation issues as a
        ``ValueError``
        """
        try:
            self.full_clean()
        except ValidationError as exc:
            raise ValueError(exc) from exc


class PerTurnModel(models.Model):
    """
    Models which represent an in entity which is has a potentially different
    state every turn should inherit from this base.
    """
    turn = models.ForeignKey(
        'Turn',
        null=False,
        related_name='%(class)s_states',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
