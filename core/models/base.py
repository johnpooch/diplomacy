from django.core.exceptions import ValidationError
from django.db import models

from core.utils.date.timespan import timespans


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
    NONE = None
    TWELVE_HOURS = timespans.TWELVE_HOURS.db_string
    TWENTY_FOUR_HOURS = timespans.TWENTY_FOUR_HOURS.db_string
    TWO_DAYS = timespans.TWO_DAYS.db_string
    THREE_DAYS = timespans.THREE_DAYS.db_string
    FIVE_DAYS = timespans.FIVE_DAYS.db_string
    SEVEN_DAYS = timespans.SEVEN_DAYS.db_string
    CHOICES = (
        (NONE, 'None'),
        timespans.TWELVE_HOURS.as_choice,
        timespans.TWENTY_FOUR_HOURS.as_choice,
        timespans.TWO_DAYS.as_choice,
        timespans.THREE_DAYS.as_choice,
        timespans.FIVE_DAYS.as_choice,
        timespans.SEVEN_DAYS.as_choice,
    )


class DrawResponse:
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CHOICES = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )


class DrawStatus:
    PROPOSED = 'proposed'
    CANCELED = 'canceled'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    EXPIRED = 'expired'
    CHOICES = (
        (PROPOSED, 'Proposed'),
        (CANCELED, 'Canceled'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (EXPIRED, 'Expired'),
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
    RETREAT = 'retreat'
    BUILD = 'build'
    CHOICES = (
        (ORDER, 'Order'),
        (RETREAT, 'Retreat'),
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
