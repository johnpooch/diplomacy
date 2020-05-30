from django.db.models import signals
from django.dispatch import receiver

from core import models
from core.models.base import HygienicModel


@receiver(signals.pre_save)
def hygienic_model_pre_save(sender, instance, **kwargs):
    """
    Trigger pre_save_clean() method on any instance of HygienicModel being saved
    """
    if issubclass(sender, HygienicModel):
        instance.pre_save_clean(sender, **kwargs)


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
