from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from service.models.base import HygenicModel
from service.models.models import Challenge
from service.models.piece import Piece


class Command(HygenicModel):
    """
    """

    source_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=False
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='+',
        db_column="order_id",
        null=False
    )
    valid = models.BooleanField(default=True)
    success = models.BooleanField(default=True)
    # Outcome in human friendly terms
    result_message = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def clean(self):
        """
        """
        pass

    @property
    def piece(self):
        """
        Helper to get ``source_territory.piece``.
        """
        return self.source_territory.piece

    @property
    def nation(self):
        """
        Helper to get the nation of a command more easily.
        """
        return self.order.nation

    def process(self):
        """
        """
        pass

    def _friendly_piece_exists_in_source(self):
        if not self.source_territory.friendly_piece_exists(self.nation):
            raise ValidationError(_(
                f'No friendly piece exists in {self.source_territory}.'
            ))
        return True

    def _source_piece_can_reach_target(self):
        try:
            target_coast = self.target_coast
        except AttributeError:
            target_coast = None
        if not self.piece.can_reach(self.target_territory, target_coast):
            raise ValidationError(_(
                f'{self.piece.type.title()} {self.source_territory} cannot '
                f'reach {self.target_territory}.'
            ))
        return True

    def _source_piece_is_at_sea(self):
        if not self.source_territory.is_sea():
            raise ValidationError(_(
                'Cannot convoy unless piece is at sea.'
            ))
        return True

    def _specifies_target_named_coast_if_fleet(self):
        if self.target_territory.is_complex() \
                and self.source_territory.piece.is_fleet() \
                and not self.target_coast:
            raise ValidationError(_(
                'Cannot order an fleet into a complex territory without '
                'specifying a named coast.'
            ))
        return True

    def _aux_territory_occupied(self):
        if not self.aux_territory.occupied():
            raise ValidationError(_(
                f'No piece exists in {self.aux_territory}.'
            ))
        return True

    def _aux_piece_can_reach_target(self):
        if not self.aux_piece.can_reach(self.target_territory):
            raise ValidationError(_(
                f'{self.aux_piece.type.title()} {self.aux_territory} cannot '
                f'reach {self.target_territory}.'
            ))
        return True

    def _piece_has_been_dislodged(self):
        if not self.piece.dislodged():
            raise ValidationError(_(
                'Only pieces which have been dislodged can retreat.'
            ))
        return True

    def _target_territory_not_occupied(self):
        if self.target_territory.occupied():
            raise ValidationError(_(
                'Dislodged piece cannot move to occupied territory.'
            ))
        return True

    def _target_territory_not_where_attacker_came_from(self):
        if self.target_territory == self.piece.dislodged_by\
                .get_previous_territory():
            raise ValidationError(_(
                'Dislodged piece cannot move to territory from which '
                'attacking piece came.'
            ))
        return True

    def _target_not_vacant_by_standoff_on_previous_turn(self):
        if self.target_territory.standoff_occured_on_previous_turn():
            raise ValidationError(_(
                'Dislodged piece cannot move to territory where a standoff '
                'occured on the previous turn.'
            ))
        return True


class TargetTerritoryMixin(models.Model):
    """
    """
    target_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=False,
    )

    class Meta:
        abstract = True


class TargetCoastMixin(models.Model):
    """
    """
    target_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class AuxTerritoryMixin(models.Model):
    """
    """
    aux_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='+',
        null=False,
    )

    class Meta:
        abstract = True

    @property
    def aux_piece(self):
        return self.aux_territory.piece


class Hold(Command):

    def clean(self):
        return self._friendly_piece_exists_in_source(),


class Build(Command):

    source_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True
    )
    piece_type = models.CharField(
        max_length=50,
        null=False,
        choices=Piece.PieceType.CHOICES,
    )

    def clean(self):

        # check territory is not occupied
        if self.source_territory.occupied():
            raise ValidationError(_(
                'Cannot build in occupied territory.'
            ))
        # check source territory has supply center
        if not self.source_territory.has_supply_center():
            raise ValidationError(_(
                'Cannot build in a territory that does not have a supply '
                'center.'
            ))
        # check source territory nationality
        if not self.source_territory.supply_center.nationality == self.nation:
            raise ValidationError(_(
                'Cannot build in supply centers outside of home territory.'
            ))
        # check source territory nationality
        if not self.source_territory.controlled_by == self.nation:
            raise ValidationError(_(
                'Cannot build in supply centers which are not controlled by '
                'nation.'
            ))
        # cannot build fleet inland
        if self.source_territory.is_inland() and \
                self.piece_type == Piece.PieceType.FLEET:
            raise ValidationError(_(
                'Cannot build fleet in inland territory.'
            ))
        return True


class Disband(Command):

    def clean(self):
        return self._friendly_piece_exists_in_source(),


class Move(Command, TargetCoastMixin, TargetTerritoryMixin):
    """
    """

    class Meta:
        db_table = 'move'

    def clean(self):
        """
        """
        return all([
            self._friendly_piece_exists_in_source(),
            self._source_piece_can_reach_target(),
            self._specifies_target_named_coast_if_fleet(),
        ])

    def process(self):
        """
        """
        Challenge.objects.create(
            piece=self.source_territory.piece,
            territory=self.target_territory
        )


class Support(Command, AuxTerritoryMixin, TargetTerritoryMixin):
    """
    """

    class Meta:
        db_table = 'support'

    @property
    def aux_piece(self):
        return self.aux_territory.piece

    def clean(self):
        """
        """
        return all([
            self._friendly_piece_exists_in_source(),
            self._source_piece_can_reach_target(),
            self._aux_territory_occupied(),
            self._aux_piece_can_reach_target(),
        ])

    def process(self):
        """
        """
        pass


class Convoy(Command, AuxTerritoryMixin, TargetTerritoryMixin):
    """
    """
    class Meta:
        db_table = 'convoy'

    def clean(self):
        """
        """
        return all([
            self._friendly_piece_exists_in_source(),
            self._aux_territory_occupied(),
            self._aux_piece_can_reach_target(),
            self._source_piece_is_at_sea(),
        ])


class Retreat(Command, TargetCoastMixin, TargetTerritoryMixin):
    """
    """
    class Meta:
        db_table = 'retreat'

    def clean(self):
        """
        """
        return all([
            self._friendly_piece_exists_in_source(),
            self._source_piece_can_reach_target(),
            self._specifies_target_named_coast_if_fleet(),
            self._piece_has_been_dislodged(),
            self._target_territory_not_occupied(),
            self._target_territory_not_where_attacker_came_from(),
            self._target_not_vacant_by_standoff_on_previous_turn(),
        ])

    def process(self):
        """
        """
        Challenge.objects.create(
            piece=self.source_territory.piece,
            territory=self.target_territory
        )
