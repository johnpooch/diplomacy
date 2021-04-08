from django.contrib.auth.models import User
from django.db import models

from core.models.base import SurrenderStatus


class Surrender(models.Model):
    """
    Represent a game participant's decision to surrender from the game. After
    the participant has decided to surrender, they have until the end of the
    turn or until another player replaces them to cancel the surrender.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='surrenders',
    )
    nation_state = models.ForeignKey(
        'NationState',
        on_delete=models.CASCADE,
        related_name='surrenders',
    )
    status = models.CharField(
        max_length=20,
        choices=SurrenderStatus.CHOICES,
        default=SurrenderStatus.PENDING,
        null=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    replaced_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='replaced',
        null=True,
    )
    # The time at which the surrender was canceled or fulfilled
    resolved_at = models.DateTimeField(
        null=True,
    )
