from django.db.models import signals
from django.dispatch import receiver

from core import models
from core.models.mixins import AutoSlug
from core.utils.models import super_receiver


@receiver(signals.pre_save, sender=models.Turn)
def set_to_current_turn(sender, instance, **kwargs):
    """
    Set game's current turn to `current_turn=False` before creating new turn.
    """
    try:
        old_turn = instance.game.get_current_turn()
        if not old_turn == instance:
            old_turn.current_turn = False
            old_turn.save()
    except models.Turn.DoesNotExist:
        pass


@super_receiver(signals.pre_save, base_class=AutoSlug)
def add_automatic_slug(sender, instance, **kwargs):
    """
    Fill the slug field on models inheriting from AutoSlug on pre-save.
    """
    instance.hydrate_slug()
