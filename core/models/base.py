from django.core.exceptions import ValidationError
from django.db import models


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
