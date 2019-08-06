from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext as _


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


class Challenge(models.Model):
    """
    """
    piece = models.OneToOneField(
        'Piece',
        on_delete=models.CASCADE,
        null=False,
        related_name='challenging',
    )
    territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        null=False,
        related_name='challenges',
    )

    class Meta:
        db_table = "challenge"


class Command(models.Model):
    """
    """
    # TODO: should make tight db constraints for different commands
    COMMAND_TYPES = (
        ('H', 'Hold'),
        ('M', 'Move'),
        ('S', 'Support'),
        ('C', 'Convoy'),
        ('R', 'Retreat'),
        ('D', 'Disband'),
        ('B', 'Build'),
    )

    class CommandType:
        HOLD = 'hold'
        MOVE = 'move'
        CHOICES = (
            (HOLD, 'Hold'),
            (MOVE, 'Fleet'),
        )

    source_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='source_commands',
        null=False,
        db_constraint=False
    )
    aux_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='aux_commands',
        null=True
    )
    target_territory = models.ForeignKey(
        'Territory',
        on_delete=models.CASCADE,
        related_name='target_commands',
        null=True
    )
    source_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True
    )
    target_coast = models.ForeignKey(
        'NamedCoast',
        on_delete=models.CASCADE,
        related_name='+',
        null=True
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='commands',
        db_column="order_id",
        null=False
    )
    type = models.CharField(
        max_length=100,
        choices=CommandType.CHOICES,
        null=False
    )
    valid = models.BooleanField(default=True)
    success = models.BooleanField(default=True)
    # Outcome in human friendly terms
    result_message = models.CharField(max_length=100, null=True)

    objects = models.Manager()

    class Meta:
        db_table = "command"

    @property
    def source_piece(self):
        """
        """
        return self.source_territory.piece

    def invalidate(self, message):
        """
        """
        self.valid = True
        self.message = message
        self.save()

    def check_valid(self):
        """
        """
        source = self.source_territory
        target = self.target_territory
        piece = source.piece

        convoy_move_is_possible = source.coastal and target.coastal

        if target not in source.neighbours.all():
            if (piece.type == piece.PieceType.ARMY and not convoy_move_is_possible):
                message = _(
                    'Army cannot move to non adjacent territory unless moving from '
                    'one coastal territory to another coastal territory.'
                )
                self.invalidate(message)
                return False

            if piece.type == piece.PieceType.FLEET:
                message = _(
                    'Fleet cannot move to non adjacent territory.'
                )
                self.invalidate(message)
                return False

        if not target.accessible_by_piece_type(piece):
            message = _('Target is not accessible by piece type.')
            self.invalidate(message)
            return False

        if (source.coastal and target.coastal) \
                and (target not in source.shared_coasts.all()) \
                and (piece.type == piece.PieceType.FLEET):
            message = _(
                'Fleet cannot move from one coastal territory to another '
                'unless both territories share a coastline.'
            )
            self.invalidate(message)
            return False

        return True


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


class SupplyCenter(models.Model):
    """
    """
    controlled_by = models.ForeignKey(
        'Nation',
        related_name='controlled_supply_centers',
        on_delete=models.CASCADE,
        db_column='nation_id',
        null=True
    )
    nationality = models.ForeignKey(
        'Nation',
        related_name='national_supply_centers',
        on_delete=models.CASCADE,
        null=True
    )
    territory = models.OneToOneField(
        'Territory',
        primary_key=True,
        on_delete=models.CASCADE,
        db_column='territory_id',
        related_name='supply_center',
        null=False
    )

    class Meta:
        db_table = "supply_center"

    def __str__(self):
        return self.territory.display_name


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
