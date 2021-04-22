import factory
from faker import Faker
from factory import lazy_attribute, post_generation
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from core import models
from core.models.base import GameStatus, OrderType, Phase, PieceType, Season
from core.utils.data import get_fixture_data

fake = Faker()

nation_data = get_fixture_data('dev/nation.json')
piece_data = get_fixture_data('dev/games/game_1/pieces.json')
territory_data = get_fixture_data('dev/territory.json')


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
    username = lazy_attribute(
        lambda o: slugify(o.first_name + '.' + o.last_name))
    email = lazy_attribute(lambda o: o.username + "@example.com")


class PieceFactory(DjangoModelFactory):
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
    supply_center = True


class NationStateFactory(DjangoModelFactory):
    class Meta:
        model = models.NationState

    nation = factory.SubFactory(NationFactory)


class TerritoryStateFactory(DjangoModelFactory):
    class Meta:
        model = models.TerritoryState

    territory = factory.SubFactory(TerritoryFactory)


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
            for participant in extracted:
                self.participants.add(participant)

    @factory.post_generation
    def turns(self, create, *args, **kwargs):
        count = 1
        make_turn = getattr(TurnFactory, 'create' if create else 'build')
        turns = [make_turn(game=self) for i in range(count)]

        if not create:
            self._prefetched_objects_cache = {'turns': turns}


class StandardTerritoryFactory(DjangoModelFactory):
    class Meta:
        model = models.Territory
        django_get_or_create = ('name',)

    name = 'Test Territory'
    controlled_by_initial = factory.SubFactory(NationFactory)
    nationality = factory.SubFactory(NationFactory)
    variant = factory.SubFactory(VariantFactory)


class StandardNationFactory(DjangoModelFactory):

    class Meta:
        model = models.Nation
        django_get_or_create = ('name',)

    name = 'Test Nation'


class StandardVariantFactory(DjangoModelFactory):

    class Meta:
        model = models.Variant

    name = 'standard'

    @post_generation
    def nations(self, create, *args, **kwargs):
        make_nation = getattr(StandardNationFactory, 'create' if create else 'build')
        nations = [make_nation(
            variant=self,
            name=nation['fields']['name'],
        ) for nation in nation_data]

        if not create:
            self._prefetched_objects_cache = {'nations': nations}

    @post_generation
    def territories(self, create, count, **kwargs):
        make_territory = getattr(StandardTerritoryFactory,
                                 'create' if create else 'build')

        territories = []
        for territory in territory_data:
            controlled_by_initial_id = territory['fields']['controlled_by_initial']

            nations = [n for n in nation_data if n['pk'] == controlled_by_initial_id]
            if nations:
                nation = nations[0]
            else:
                nation = None

            if nation:
                territories.append(
                    make_territory(
                        variant=self,
                        name=territory['fields']['name'],
                        controlled_by_initial=factory.SubFactory(
                            StandardNationFactory,
                            name=nations[0]['fields']['name']
                        ),
                        nationality=None,
                        supply_center=territory['fields'].get('supply_center', False),
                        type=territory['fields']['type'],
                        initial_piece_type=territory['fields'].get('initial_piece_type'),
                    )
                )
            else:
                territories.append(
                    make_territory(
                        variant=self,
                        name=territory['fields']['name'],
                        controlled_by_initial=None,
                        nationality=None,
                        supply_center=territory['fields'].get('supply_center', False),
                        type=territory['fields']['type'],
                        initial_piece_type=territory['fields'].get('initial_piece_type'),
                    )
                )


class StandardTurnFactory(DjangoModelFactory):

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
            self._prefetched_objects_cache = {
                'territorystates': territorystates}

    @post_generation
    def nationstates(self, create, *args, **kwargs):
        variant = self.game.variant
        make_nation_state = getattr(
            NationStateFactory,
            'create' if create else 'build',
        )
        nationstates = [
            make_nation_state(
                turn=self,
                nation=nation,
            )
            for nation in variant.nations.all()
        ]

        if not create:
            self._prefetched_objects_cache = {
                'nationstates': nationstates}

    @post_generation
    def pieces(self, create, *args, **kwargs):
        make_piece = getattr(
            PieceFactory,
            'create' if create else 'build',
        )
        pieces = []
        for piece in piece_data:
            territory = [t for t in territory_data
                         if t['pk'] == piece['fields']['territory']][0]
            p = make_piece(
                turn=self,
                territory=factory.SubFactory(
                    StandardTerritoryFactory,
                    name=territory['fields']['name']
                ),
                type=piece['fields']['type'],
            )
            pieces.append(p)

        if not create:
            self._prefetched_objects_cache = {
                'pieces': pieces}


class StandardGameFactory(DjangoModelFactory):

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

        make_turn = getattr(StandardTurnFactory,
                            'create' if create else 'build')
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
