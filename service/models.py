from django.db import models
from django.db.models import Manager, QuerySet, Sum, When, Case
from django.core.exceptions import ObjectDoesNotExist


class Announcement(models.Model):
    """
    """
    nation = models.ForeignKey('Nation', related_name='announcements',
            on_delete=models.CASCADE, null=False)
    text = models.CharField(max_length=1000, null=False)


class CurrentCommandManager(Manager):
    
    def get_queryset(self):
        """
        """
        queryset = super().get_queryset().filter(order__turn__current_turn=True)
        return queryset


class Command(models.Model):
    """
    """
    class Meta:
        db_table = "command"

    COMMAND_TYPES = (
       ('H', 'Hold'),
       ('M', 'Move'),
       ('S', 'Support'),
       ('C', 'Convoy'),
       ('R', 'Retreat'),
       ('D', 'Disband'),
       ('B', 'Build'),
    )

    objects = models.Manager()
    current_turn_commands = CurrentCommandManager()

    source_territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            related_name='source_commands', null=False, db_constraint=False)
    target_territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            related_name='target_commands', null=True)
    aux_territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            related_name='aux_commands', null=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE,
            related_name='commands', db_column="order_id", null=False)
    type = models.CharField(max_length=1, choices=COMMAND_TYPES, null=False)
    successful = models.BooleanField(default=True)
    # Outcome in human friendly terms
    result_message = models.CharField(max_length=100, null=True)

    def fail(self, result_message):
        command.success = False
        command.result_message = result_message
        command.save()


class Game(models.Model):
    """
    """
    class Meta:
        db_table = "game"

    name = models.CharField(max_length=50, null=False)


class Message(models.Model):
    """
    """
    class Meta:
        db_table = "message"

    sender = models.ForeignKey('Nation', related_name='sent_messages',
            on_delete=models.CASCADE, null=False)
    recipient = models.ForeignKey('Nation', related_name='received_messages',
            on_delete=models.CASCADE, null=False)
    text = models.CharField(max_length=1000, null=False)


class Nation(models.Model):
    """
    """
    class Meta:
        db_table = "nation"

    name = models.CharField(max_length=15)
    active = models.BooleanField(default=True)

    def has_pieces_which_must_retreat(self):
        return any([piece.must_retreat for piece in self.pieces.all()])

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    """
    class Meta:
        db_table = "order"

    nation = models.ForeignKey('Nation', related_name='orders',
            on_delete=models.CASCADE, db_column="nation_id", null=False,
            db_constraint=False)
    turn = models.ForeignKey('Turn', on_delete=models.CASCADE, null=False)
    finalised = models.BooleanField(default=False)


class Piece(models.Model):
    """
    """

    PIECE_TYPES = (
        ('A', 'Army'),
        ('F', 'Fleet'),
    )

    class Meta:
        db_table = "piece"

    nation = models.ForeignKey('Nation', related_name='pieces',
            on_delete=models.CASCADE, db_column="nation_id", null=False,
            db_constraint=False)
    type = models.CharField(max_length=1, choices=PIECE_TYPES, null=False)
    territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            db_column='territory_id', related_name='pieces', null=True)
    challenging = models.ForeignKey('Territory', on_delete=models.SET_NULL,
            db_column='challenging_territory_id',
            related_name='challenging_pieces', null=True)
    must_retreat = models.BooleanField(default=False)
    must_disband = models.BooleanField(default=False)
    active = models.BooleanField(default=True)


    def __str__(self):
        return ' '.join([self.get_type_display(), self.territory.display_name])


class Phase(models.Model):
    """
    """
    class Meta:
        db_table = "phase"

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


    def __str__(self):
        return " ".join([self.get_type_display(), self.get_season_display()])


class SupplyCenter(models.Model):
    """
    """
    class Meta:
        db_table = "supply_center"

    controlled_by = models.ForeignKey('Nation',
            related_name='controlled_supply_centers', on_delete=models.CASCADE,
            db_column='nation_id', null=True)
    nationality = models.ForeignKey('Nation',
            related_name='national_supply_centers',
            on_delete=models.CASCADE, null=True)
    territory = models.OneToOneField('Territory', primary_key=True,
            on_delete=models.CASCADE, db_column='territory_id',
            related_name='supply_center', null=False)

    def __str__(self):
        return self.territory.display_name


class Territory(models.Model):
    """
    """

    class Meta:
        db_table = "territory"

    TERRITORY_TYPES = (
        ('L', 'Land'),
        ('S', 'Sea'),
    )

    abbreviation = models.CharField(max_length=6, null=False)
    display_name = models.CharField(max_length=50, null=False)
    controlled_by = models.ForeignKey('Nation', on_delete=models.CASCADE,
            db_column='controlled_by_id', null=True,
            related_name='controlled_territories',)
    neighbours = models.ManyToManyField('self', blank=True)
    shared_coasts = models.ManyToManyField('self', related_name='shared_coasts',
            blank=True)
    type = models.CharField(max_length=10, choices=TERRITORY_TYPES, null=False)
    coast = models.BooleanField(default=False)

    def is_neighbour(self, territory):
        return territory in self.neighbours.all()

    def get_piece(self):
        """
        Return the piece if it exists in the territory. If no piece exists
        in the territory, return False. If more than one piece exists in the
        territory, throw an error.
        """
        if self.pieces.all().count() == 1:
            return self.pieces.all()[0]
        if self.pieces.all().count() > 1:
            raise ValueError((f"More than one piece exists in {self}. "
                    "There should never be more than one piece in a territory "
                    "except when retreating or disbanding."))
        return False

    def get_friendly_piece(self, nation):
        """
        Get piece belonging to nation if exists in territory.
        """
        for piece in self.pieces.all():
            if piece.nation == nation:
                return piece
        return False

    def accessible_by_piece_type(self, piece):
        """
        Armies cannot enter sea territories. Fleets cannot enter non-coastal
        land territories.
        """
        if piece.type == 'A':
            return self.type == 'L'
        return self.type == 'S' or self.coast

    def has_supply_center(self):
        try:
            return bool(self.supply_center)
        except ObjectDoesNotExist:
            return False

    def __str__(self):
        return self.display_name.capitalize()


class TurnManager(Manager):
    
    def get_queryset(self):
        """
        """
        queryset = super().get_queryset()
        return queryset


class Turn(models.Model):
    """
    """
    objects = TurnManager()

    class Meta:
        db_table = "turn"

    year = models.IntegerField()
    phase = models.ForeignKey('Phase', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)
    current_turn = models.BooleanField(default=True)

    def __str__(self):
        return " ".join([str(self.phase), str(self.year)])

