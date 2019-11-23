from django.db import models


class Announcement(models.Model):
    """
    This is a message that can be read by all players in the game.
    """
    nation = models.ForeignKey(
        'Nation',
        related_name='announcements',
        on_delete=models.CASCADE,
        null=False
    )
    text = models.CharField(
        max_length=1000,
        null=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "announcement"


class Message(models.Model):
    """
    This is a message that can only be read by the recipient.
    """
    sender = models.ForeignKey(
        'Nation',
        related_name='sent_messages',
        on_delete=models.CASCADE,
        null=False
    )
    recipient = models.ForeignKey(
        'Nation',
        related_name='received_messages',
        on_delete=models.CASCADE,
        null=False
    )
    text = models.CharField(
        max_length=1000,
        null=False,
    )

    class Meta:
        db_table = "message"
