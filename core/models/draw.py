from django.contrib.auth.models import User
from django.db import models

from core.models.base import PerTurnModel, DrawResponse, DrawStatus


class Draw(PerTurnModel):
    """
    Represents a proposed draw.

    The proposed victors must have enough supply centers to win. There must be
    at least two nations in a draw and each variant defines a maximum number of
    nations in a draw.

    A draw must be accepted by all nations in the game (not including nations
    in civil disorder). If the turn ends and all players have not accepted the
    draw, the draw will be unsuccessful and the game will continue.

    If all players accept the draw by the end of the turn, the draw will be
    accepted and the included nations will win the game.

    If all players reject the draw by the end of the turn, the draw will be
    rejected.
    """
    proposed_by = models.ForeignKey(
        'Nation',
        on_delete=models.CASCADE,
        related_name='proposed_draws',
    )
    proposed_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    proposed_at = models.DateTimeField(
        auto_now_add=True,
    )
    nations = models.ManyToManyField(
        'Nation',
        related_name='draws',
    )
    status = models.CharField(
        max_length=20,
        choices=DrawStatus.CHOICES,
        default=DrawStatus.PROPOSED,
        null=False,
    )
    resolved_at = models.DateTimeField(
        null=True,
    )

    def __str__(self):
        return '{} - [{}] - {}'.format(
            self.proposed_by.name,
            ', '.join(self.nations.all().values_list('name', flat=True)),
            self.get_status_display()
        )

    def set_status(self):
        """
        Check if the draw has received all responses necessary to update the
        status of the draw.
        """
        if self.status != DrawStatus.PROPOSED:
            raise ValueError(
                'Cannot call set_status on Draw instance that is already '
                'resolved.'
            )
        if self._has_enough_responses() and self._responses_unanimous():
            self.status = self.drawresponse_set.first().response
            self.save()
        return self.status

    def _has_enough_responses(self):
        num_responses_required = (
            self.turn.nationstates.exclude_civil_disorder().count()
        )
        return self.drawresponse_set.count() >= num_responses_required

    def _responses_unanimous(self):
        values = self.drawresponse_set.all().values_list('response', flat=True)
        return all(v == values[0] for v in values)


class DrawResponse(models.Model):
    draw = models.ForeignKey(
        'Draw',
        on_delete=models.CASCADE,
    )
    nation = models.ForeignKey(
        'Nation',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    response = models.CharField(
        max_length=20,
        choices=DrawResponse.CHOICES,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        unique_together = ['draw', 'nation']
