import factory
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User

from core import models


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

    username = 'test user'


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
