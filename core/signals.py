from django.db.models import signals
from django.dispatch import receiver

from core.models.base import HygenicModel


@receiver(signals.pre_save)
def hygenic_model_pre_save(sender, instance, **kwargs):
    """
    Trigger pre_save_clean() method on any instance of HygenicModel being saved
    """
    if issubclass(sender, HygenicModel):
        instance.pre_save_clean(sender, **kwargs)
