from django.test import TestCase

from core import models


class InitialGameStateTestCase(TestCase):
    """
    """
    def setUp(self):
        # Game State
        self.game = models.Game.objects.create(
            name='test game',
        )
        self.phase = models.Phase.objects.create(
            season='S',
            type='O',
        )
        self.turn = models.Turn.objects.create(
            year=1900,
            phase=self.phase,
            game=self.game,
            current_turn=True,
        )


class TerritoriesMixin:

    def initialise_territories(self):
        self.belgium = models.Territory.objects.get(name='belgium')
        self.brest = models.Territory.objects.get(name='brest')
        self.burgundy = models.Territory.objects.get(name='burgundy')
        self.english_channel = models.Territory.objects.get(name='english channel')
        self.edinburgh = models.Territory.objects.get(name='edinburgh')
        self.gascony = models.Territory.objects.get(name='gascony')
        self.gulf_of_lyon = models.Territory.objects.get(name='gulf of lyon')
        self.holland = models.Territory.objects.get(name='holland')
        self.irish_sea = models.Territory.objects.get(name='irish sea')
        self.kiel = models.Territory.objects.get(name='kiel')
        self.london = models.Territory.objects.get(name='london')
        self.marseilles = models.Territory.objects.get(name='marseilles')
        self.mid_atlantic = models.Territory.objects.get(name='mid atlantic')
        self.munich = models.Territory.objects.get(name='munich')
        self.north_atlantic = models.Territory.objects.get(name='north atlantic')
        self.north_sea = models.Territory.objects.get(name='north sea')
        self.norwegian_sea = models.Territory.objects.get(name='norwegian sea')
        self.paris = models.Territory.objects.get(name='paris')
        self.picardy = models.Territory.objects.get(name='picardy')
        self.piedmont = models.Territory.objects.get(name='piedmont')
        self.portugal = models.Territory.objects.get(name='portugal')
        self.silesia = models.Territory.objects.get(name='silesia')
        self.spain = models.Territory.objects.get(name='spain')
        self.st_petersburg = models.Territory.objects.get(name='st. petersburg')
        self.wales = models.Territory.objects.get(name='wales')
        self.western_mediterranean = models.Territory.objects.get(
            name='western mediterranean'
        )


class HelperMixin:

    def set_piece_territory(self, piece, territory, named_coast=None):
        """
        """
        piece.territory = territory
        piece.named_coast = named_coast
        piece.save()

    def hold(self, source):
        """
        """
        pass
        # return Hold(
        #     source=source,
        #     order=self.order,
        # )

    def move(self, source, target, target_coast=None):
        """
        """
        return models.Command(
            source=source,
            target=target,
            order=self.order,
            target_coast=target_coast,
            type=models.Command.Types.MOVE,
        )

    def support(self, source, target, aux):
        """
        """
        return models.Command(
            source=source,
            target=target,
            aux=aux,
            order=self.order,
            type=models.Command.Types.SUPPORT,
        )

    def convoy(self, source, target, aux):
        """
        """
        return models.Command(
            source=source,
            target=target,
            aux=aux,
            order=self.order,
            type=models.Command.Types.CONVOY,
        )

    def build(self, target, piece_type, target_coast=None):
        """
        """
        return models.Command(
            target=target,
            target_coast=target_coast,
            piece_type=piece_type,
            order=self.order,
            type=models.Command.Types.BUILD
        )
