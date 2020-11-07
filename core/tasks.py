from celery import shared_task
from django.db import transaction

from . import models


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
            turn.process(processed_at)
    except Exception:
        pass
    finally:
        models.TurnEnd.objects.filter(turn=turn).delete()
