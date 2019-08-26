from django.test import TestCase

from service.models import Move, Game, Order, Phase, Territory, Turn


class InitialGameStateTestCase(TestCase):
    """
    """
    def setUp(self):
        # Game State
        self.game = Game.objects.create(
            name='test game',
        )
        self.phase = Phase.objects.create(
            season='S',
            type='O',
        )
        self.turn = Turn.objects.create(
            year=1900,
            phase=self.phase,
            game=self.game,
            current_turn=True,
        )


class TerritoriesMixin:

    def initialise_territories(self):
        self.belgium = Territory.objects.get(name='belgium')
        self.brest = Territory.objects.get(name='brest')
        self.burgundy = Territory.objects.get(name='burgundy')
        self.english_channel = Territory.objects.get(name='english channel')
        self.gascony = Territory.objects.get(name='gascony')
        self.gulf_of_lyon = Territory.objects.get(name='gulf of lyon')
        self.holland = Territory.objects.get(name='holland')
        self.irish_sea = Territory.objects.get(name='irish sea')
        self.kiel = Territory.objects.get(name='kiel')
        self.london = Territory.objects.get(name='london')
        self.marseilles = Territory.objects.get(name='marseilles')
        self.mid_atlantic = Territory.objects.get(name='mid atlantic')
        self.paris = Territory.objects.get(name='paris')
        self.picardy = Territory.objects.get(name='picardy')
        self.piedmont = Territory.objects.get(name='piedmont')
        self.silesia = Territory.objects.get(name='silesia')
        self.spain = Territory.objects.get(name='spain')
        self.wales = Territory.objects.get(name='wales')
        self.western_mediterranean = Territory.objects.get(name='western mediterranean')


class HelperMixin:

    def set_piece_territory(self, piece, territory, named_coast=None):
        """
        """
        piece.territory = territory
        piece.named_coast = named_coast
        piece.save()

    def move(self, source, target, source_coast=None, target_coast=None):
        """
        """
        return Move(
            source_territory=source,
            target_territory=target,
            order=self.order,
            source_coast=source_coast,
            target_coast=target_coast,
        )

    def support_command(self, source, target, aux,
                            source_coast=None, target_coast=None):
        """
        """
        return Command(
            source_territory=source,
            target_territory=target,
            aux_territory=aux,
            order=self.order,
            type=Command.CommandType.SUPPORT,
            source_coast=source_coast,
            target_coast=target_coast,
        )
