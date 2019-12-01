from django.core.exceptions import ValidationError
from django.db import models


class NationChoiceMode:
    RANDOM = 'random'
    PREFERENCE = 'preference'
    FIRST_COME = 'first come'
    CHOICES = (
        (RANDOM, 'Random'),
        (PREFERENCE, 'Preference'),
        (FIRST_COME, 'First come first serve')
    )


class DeadlineFrequency:
    TWELVE_HOURS = 'twelve hours'
    TWENTY_FOUR_HOURS = 'twenty four hours'
    TWO_DAYS = 'two days'
    THREE_DAYS = 'three days'
    FIVE_DAYS = 'five days'
    SEVEN_DAYS = 'seven days'
    CHOICES = (
        (TWELVE_HOURS, '12 hours'),
        (TWENTY_FOUR_HOURS, '24 hours'),
        (TWO_DAYS, '2 days'),
        (THREE_DAYS, '3 days'),
        (FIVE_DAYS, '5 days'),
        (SEVEN_DAYS, '7 days'),
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


class GameStatus:
    PENDING = 'pending'
    ACTIVE = 'active'
    ENDED = 'ended'
    CHOICES = (
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (ENDED, 'Ended'),
    )


class OrderState:
    UNRESOLVED = 'unresolved'
    SUCCEEDS = 'succeeds'
    FAILS = 'fails'
    CHOICES = (
        (UNRESOLVED, 'Unresolved'),
        (SUCCEEDS, 'Succeeds'),
        (FAILS, 'Fails')
    )


class OrderType:
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


class OutcomeType:
    RESOLVED = 'resolved'
    BOUNCED = 'bounced'
    ILLEGAL = 'illegal'
    AUX_FAILED = 'aux failed'
    AUX_DOES_NOT_CORRESPOND = 'aux does not correspond'
    CHOICES = (
        (RESOLVED, 'Resolved'),
        (BOUNCED, 'Bounced'),
        (ILLEGAL, 'Illegal'),
        (AUX_FAILED, 'Aux failed'),
        (AUX_DOES_NOT_CORRESPOND, 'Aux does not correspond'),
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


class PieceType:
    ARMY = 'army'
    FLEET = 'fleet'
    CHOICES = (
        (ARMY, 'Army'),
        (FLEET, 'Fleet'),
    )


class Season:
    FALL = 'fall'
    SPRING = 'spring'
    CHOICES = (
        (FALL, 'Fall'),
        (SPRING, 'Spring'),
    )


class TerritoryType:
    LAND = 'land'
    SEA = 'sea'
    CHOICES = (
        (LAND, 'Land'),
        (SEA, 'Sea'),
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
        related_name='%(class)ss',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
