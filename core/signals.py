from django.db.models import signals
from django.dispatch import receiver

from core.models.base import HygienicModel


@receiver(signals.pre_save)
def hygienic_model_pre_save(sender, instance, **kwargs):
    """
    Trigger pre_save_clean() method on any instance of HygienicModel being saved
    """
    if issubclass(sender, HygienicModel):
        instance.pre_save_clean(sender, **kwargs)
