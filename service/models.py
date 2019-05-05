from django.db import models


PIECE_TYPES = (
    ('A', 'Army'),
    ('F', 'Fleet'),
)


class Announcement(models.Model):
    """
    """
    nation = models.ForeignKey('Nation', related_name='announcements',
            on_delete=models.CASCADE, null=False)
    text = models.CharField(max_length=1000, null=False)


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
    source_territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            related_name='source_commands', null=False, db_constraint=False)
    target_territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            related_name='target_commands', null=True)
    aux_territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            related_name='aux_commands', null=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE,
            related_name='commands', db_column="order_id", null=False)
    type = models.CharField(max_length=1, choices=COMMAND_TYPES, null=False)

    def validate_command(self):
        # check source territory contains piece belonging to player
        pass
        

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
    class Meta:
        db_table = "piece"

    nation = models.ForeignKey('Nation', related_name='pieces',
            on_delete=models.CASCADE, db_column="nation_id", null=False,
            db_constraint=False)
    type = models.CharField(max_length=1, choices=PIECE_TYPES, null=False)
    territory = models.ForeignKey('Territory', on_delete=models.CASCADE,
            db_column='territory_id', null=True)
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
        ('M', 'Move'),
        ('B', 'Build'),
        ('R', 'Retreat'),
        ('D', 'Disband'),
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

    owner = models.ForeignKey('Nation',
            related_name='controlled_supply_centers', on_delete=models.CASCADE,
            db_column='nation_id', null=True)
    nationality = models.ForeignKey('Nation',
            related_name='national_supply_centers',
            on_delete=models.CASCADE, null=True)
    territory = models.ForeignKey('Territory', related_name='supply_center',
            on_delete=models.CASCADE, db_column='territory_id', null=False)

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

    def __str__(self):
        return self.display_name


class Turn(models.Model):
    """
    """
    class Meta:
        db_table = "turn"

    year = models.IntegerField()
    phase = models.ForeignKey('Phase', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return " ".join([str(self.phase), str(self.year)])

