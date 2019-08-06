from service.models import Territory


class TerritoriesMixin:

    def initialise_territories(self):
        self.brest = Territory.objects.get(name='brest')
        self.burgundy = Territory.objects.get(name='burgundy')
        self.english_channel = Territory.objects.get(name='english channel')
        self.gascony = Territory.objects.get(name='gascony')
        self.gulf_of_lyon = Territory.objects.get(name='gulf of lyon')
        self.irish_sea = Territory.objects.get(name='irish sea')
        self.marseilles = Territory.objects.get(name='marseilles')
        self.mid_atlantic = Territory.objects.get(name='mid atlantic')
        self.paris = Territory.objects.get(name='paris')
        self.picardy = Territory.objects.get(name='picardy')
        self.piedmont = Territory.objects.get(name='piedmont')
        self.silesia = Territory.objects.get(name='silesia')
        self.spain = Territory.objects.get(name='spain')
