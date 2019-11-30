import factory
from faker import Faker
from factory import DjangoModelFactory, lazy_attribute, post_generation

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from core import models
from core.models.base import GameStatus, OrderType, Phase, PieceType, Season
from core.utils.data import get_territory_data


fake = Faker()

class VariantFactory(DjangoModelFactory):

    class Meta:
        model = models.Variant

    name = 'standard'


class NationFactory(DjangoModelFactory):

    class Meta:
        model = models.Nation

    name = 'Test Nation'
    variant = factory.SubFactory(VariantFactory)


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = ('username',)

    first_name = lazy_attribute(lambda o: fake.first_name())
    last_name = lazy_attribute(lambda o: fake.last_name())
    username = lazy_attribute(lambda o: slugify(o.first_name + '.' + o.last_name))
    email = lazy_attribute(lambda o: o.username + "@example.com")


class ArmyFactory(DjangoModelFactory):

    class Meta:
        model = models.Piece

    nation = factory.SubFactory(NationFactory)
    type = PieceType.ARMY


class OrderFactory(DjangoModelFactory):

    class Meta:
        model = models.Order

    type = OrderType.HOLD
    nation = factory.SubFactory(NationFactory)


class TerritoryFactory(DjangoModelFactory):

    class Meta:
        model = models.Territory

    name = 'Test Territory'
    controlled_by_initial = factory.SubFactory(NationFactory)
    nationality = factory.SubFactory(NationFactory)
    variant = factory.SubFactory(VariantFactory)


class TerritoryStateFactory(DjangoModelFactory):

    class Meta:
        model = models.TerritoryState


class TurnFactory(DjangoModelFactory):

    class Meta:
        model = models.Turn

    year = '1900'
    season = Season.SPRING
    phase = Phase.ORDER


class GameFactory(DjangoModelFactory):

    class Meta:
        model = models.Game

    variant = factory.SubFactory(VariantFactory)
    created_by = factory.SubFactory(UserFactory)
    name = 'Test Game'
    num_players = 7

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of participants were passed in, use them
            for participant in extracted:
                self.participants.add(participant)


class StandardVariantFactory(DjangoModelFactory):
    """
    Creates the standard variant and the territories of that variant.
    """
    class Meta:
        model = models.Variant

    name = 'standard'

    @post_generation
    def territories(self, create, count, **kwargs):
        make_territory = getattr(TerritoryFactory, 'create' if create else 'build')
        territory_data = get_territory_data()
        territories = [make_territory(
            variant=self,
            name=territory['fields']['name'],
        ) for territory in territory_data]

        if not create:
            self._prefetched_objects_cache = {'territories': territories}


class StandardTurnFactory(DjangoModelFactory):
    """
    Creates a turn in the the standard diplomacy variant.
    """
    class Meta:
        model = models.Turn

    year = '1900'
    season = Season.SPRING
    phase = Phase.ORDER

    @post_generation
    def territorystates(self, create, *args, **kwargs):
        variant = self.game.variant
        make_territory_state = getattr(
            TerritoryStateFactory,
            'create' if create else 'build',
        )
        territorystates = [
            make_territory_state(
                turn=self,
                territory=territory,
                controlled_by=territory.controlled_by_initial,
            )
            for territory in variant.territories.all()
        ]

        if not create:
            self._prefetched_objects_cache = {'territorystates': territorystates}


class StandardGameFactory(DjangoModelFactory):
    """
    Creates the initial state of a standard game of diplomacy.
    """
    class Meta:
        model = models.Game

    variant = factory.SubFactory(StandardVariantFactory)
    created_by = factory.SubFactory(UserFactory)

    name = 'Factory Generated Game'
    status = GameStatus.ACTIVE
    description = lazy_attribute(lambda o: fake.text())
    num_players = 7

    @post_generation
    def turns(self, create, count, **kwargs):
        if count is None:
            count = 1

        make_turn = getattr(StandardTurnFactory, 'create' if create else 'build')
        turns = [make_turn(game=self) for i in range(count)]

        if not create:
            self._prefetched_objects_cache = {'turns': turns}

    @post_generation
    def participants(self, create, count, **kwargs):
        if count is None:
            count = 7

        make_user = getattr(UserFactory, 'create' if create else 'build')
        participants = [make_user() for i in range(count)]

        for participant in participants:
            self.participants.add(participant)
