from django.conf import settings
from django.core.mail import send_mail
from django.db.models import signals
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import slugify

from django_rest_passwordreset.signals import reset_password_token_created

from core import models
from core.models.base import DrawStatus, GameStatus
from core.models.mixins import AutoSlug
from core.utils.models import super_receiver
from project.celery import app


def set_id(instance):
    """
    In tests we don't want to have to manually set the id when creating
    nations and territories. This combines the instance name and the variant
    name to create the id automatically before saving.
    """
    time = str(timezone.now())
    instance.id = slugify(
        '-'.join(['test', instance.variant.name, instance.name, time])
    )


@receiver(signals.pre_save, sender=models.Turn)
def set_to_current_turn(sender, instance, **kwargs):
    """
    Set game's current turn to `current_turn=False` before creating new turn.
    """
    old_turn = instance.game.get_current_turn()
    if old_turn:
        if not old_turn == instance:
            old_turn.current_turn = False
            old_turn.save()


@super_receiver(signals.pre_save, base_class=AutoSlug)
def add_automatic_slug(sender, instance, **kwargs):
    """
    Fill the slug field on models inheriting from AutoSlug on pre-save.
    """
    instance.hydrate_slug()


@receiver(signals.pre_save, sender=models.Nation)
def set_nation_id_if_not_set(sender, instance, **kwargs):
    if not instance.id:
        set_id(instance)


@receiver(signals.pre_save, sender=models.Territory)
def set_territory_id_if_not_set(sender, instance, **kwargs):
    if not instance.id:
        set_id(instance)


@receiver(signals.post_save, sender=models.DrawResponse)
def set_draw_status_once_all_responses_submitted(sender, instance, **kwargs):
    if instance.draw.status == DrawStatus.PROPOSED:
        instance.draw.set_status()


@receiver(signals.post_save, sender=models.Draw)
def set_game_state_if_draw_accepted(sender, instance, **kwargs):
    game = instance.turn.game
    if instance.status == DrawStatus.ACCEPTED and game.status != GameStatus.ENDED:
        nations = [*instance.nations.all(), instance.proposed_by]
        game.set_winners(*nations)


@receiver(signals.pre_delete, sender=models.TurnEnd)
def revoke_task_on_delete(sender, instance, **kwargs):
    app.control.revoke(instance.task_id)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens. When a token is created, an e-mail is to
    be sent to the user.

    Args:
        * `sender` - View Class that sent the signal
        * `instance` -  View Instance that sent the signal
        * `reset_password_token` - Token Model Object
    """
    # send an e-mail to the user
    reset_password_url = settings.CLIENT_URL + '/reset-password/'
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            reset_password_url,
            reset_password_token.key
        )
    }

    # render email text
    html_template = 'user_reset_password.html'
    text_template = 'user_reset_password.txt'
    email_html_message = render_to_string(html_template, context)
    email_plaintext_message = render_to_string(text_template, context)

    send_mail(
        'Password Reset for {title}'.format(title='diplomacy.gg'),
        email_plaintext_message,
        getattr(settings, 'DIPLOMACY_EMAIL_FROM_ADDRESS', 'noreply@diplomacy.gg'),
        [reset_password_token.user.email],
        fail_silently=False,
        html_message=email_html_message,
    )
