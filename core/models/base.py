from django.core.exceptions import ValidationError
from django.db import models


class NationChoiceMode:
    RANDOM = 'random'
    PREFERENCE = 'preference'
    FIRST_COME = 'first_come'
    CHOICES = (
        (RANDOM, 'Random'),
        (PREFERENCE, 'Preference'),
        (FIRST_COME, 'First come first serve')
    )


class DeadlineFrequency:
    TWELVE_HOURS = 'twelve_hours'
    TWENTY_FOUR_HOURS = 'twenty_four_hours'
    TWO_DAYS = 'two_days'
    THREE_DAYS = 'three_days'
    FIVE_DAYS = 'five_days'
    SEVEN_DAYS = 'seven_days'
    CHOICES = (
        (TWELVE_HOURS, '12 hours'),
        (TWENTY_FOUR_HOURS, '24 hours'),
        (TWO_DAYS, '2 days'),
        (THREE_DAYS, '3 days'),
        (FIVE_DAYS, '5 days'),
        (SEVEN_DAYS, '7 days'),
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
    MOVES = 'moves'
    RESOLVED = 'resolved'
    BOUNCED = 'bounced'
    AUX_FAILED = 'aux_failed'
    AUX_DOES_NOT_CORRESPOND = 'aux_does_not_correspond'
    SUCCEEDS = 'succeeds'
    GIVEN = 'given'
    FAILS = 'fails'
    CHOICES = (
        (MOVES, 'Moves'),
        (RESOLVED, 'Resolved'),
        (BOUNCED, 'Bounced'),
        (AUX_FAILED, 'Aux failed'),
        (AUX_DOES_NOT_CORRESPOND, 'Aux does not correspond'),
        (SUCCEEDS, 'Succeeds'),
        (GIVEN, 'Given'),
        (FAILS, 'Fails'),
    )


class TerritoryType:
    INLAND = 'inland'
    COASTAL = 'coastal'
    SEA = 'sea'
    CHOICES = (
        (INLAND, 'Inland'),
        (COASTAL, 'Coastal'),
        (SEA, 'Sea'),
    )


class TerritoryDisplayType:
    LAND = 'land'
    SEA = 'sea'
    CHOICES = (
        (LAND, 'Land'),
        (SEA, 'Sea'),
    )


class Phase:
    ORDER = 'order'
    RETREAT_AND_DISBAND = 'retreat_and_disband'
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


class SurrenderStatus:
    PENDING = 'pending'
    CANCELED = 'canceled'
    FULFILLED = 'fulfilled'
    CHOICES = (
        (PENDING, 'Pending'),
        (CANCELED, 'Canceled'),
        (FULFILLED, 'Fulfilled'),
    )


class HygienicModel(models.Model):
    """
    Models which inherit from this base will run `Model.full_clean()` before
    save (on pre_save signal). Any `ValidationError` raised during this
    operation will be re-raised as a `ValueError`, causing the save operation
    to fail.

    This class relies upon the `hygienic_model_pre_save()` function
    in `core.signals` module to work properly.
    """
    class Meta:
        abstract = True

    def pre_save_clean(self, sender, **kwargs):
        """
        Run `full_clean()` and raise any validation issues as a
        `ValueError`
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
