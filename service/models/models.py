from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext as _

from service.models.base import HygenicModel


# Create challenges based on whether the move is possible.
# Resolve challenges into outcomes


class Announcement(models.Model):
    """
    """
    nation = models.ForeignKey(
        'Nation',
        related_name='announcements',
        on_delete=models.CASCADE,
        null=False
    )
    text = models.CharField(max_length=1000, null=False)

    class Meta:
        db_table = "announcement"


class Game(models.Model):
    """
    """
    name = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "game"


class Message(models.Model):
    """
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
    text = models.CharField(max_length=1000, null=False)

    class Meta:
        db_table = "message"


class Nation(models.Model):
    # TODO should make some sort of PerGame base model.
    """
    """
    # TODO nation should have a color field
    name = models.CharField(max_length=15)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "nation"

    def has_pieces_which_must_retreat(self):
        return any([piece.must_retreat for piece in self.pieces.all()])

    def __str__(self):
        return self.name


class OrderManager(Manager):

    def get_queryset(self):
        """
        """
        queryset = super().get_queryset()
        # TODO prefetch commands
        return queryset

    def process_orders(self):
        """
        """
        queryset = super().get_queryset()
        for order in queryset.all():
            for command in order.commands.all():
                command.process()


class Order(models.Model):
    """
    """
    # TODO: use signals when all orders are submitted
    nation = models.ForeignKey(
        'Nation',
        related_name='orders',
        on_delete=models.CASCADE,
        db_column="nation_id",
        null=False,
        db_constraint=False
    )
    turn = models.ForeignKey('Turn', on_delete=models.CASCADE, null=False)
    finalised = models.BooleanField(default=False)

    objects = OrderManager()

    class Meta:
        db_table = "order"


class Phase(models.Model):
    """
    """
    SEASONS = (
        ('S', 'Spring'),
        ('F', 'Fall'),
    )
    PHASE_TYPES = (
        ('O', 'Order'),
        ('R', 'Retreat and Disband'),
        ('B', 'Build and Disband'),
    )
    season = models.CharField(max_length=1, choices=SEASONS, null=False)
    type = models.CharField(max_length=1, choices=PHASE_TYPES, null=False)

    class Meta:
        db_table = "phase"

    def __str__(self):
        return " ".join([self.get_type_display(), self.get_season_display()])


class TurnManager(Manager):

    def get_queryset(self):
        """
        """
        queryset = super().get_queryset()
        return queryset


class Turn(models.Model):
    """
    """
    year = models.IntegerField()
    phase = models.ForeignKey('Phase', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)
    current_turn = models.BooleanField(default=True)

    objects = TurnManager()

    class Meta:
        db_table = "turn"

    def __str__(self):
        return " ".join([str(self.phase), str(self.year)])
