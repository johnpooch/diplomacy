from celery import shared_task
from django.db import transaction

from . import models
from .game import process_turn as _process_turn


@shared_task
def process_turn(turn_id, processed_at):
    """
    Process the specified turn.

    Args:
        * `turn_id` - `int` - Turn ID
        * `processed_at` - `datetime` - The time at which the turn is
        processed.
    """
    turn = models.Turn.objects.get(id=turn_id)

    try:
        with transaction.atomic():
            _process_turn(turn)
    except Exception:
        pass
    finally:
        models.TurnEnd.objects.filter(turn=turn).delete()
