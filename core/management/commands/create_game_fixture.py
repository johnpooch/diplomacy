from django.core.management.base import BaseCommand
from django.db import transaction

from core import models
from fixtures.recipe import recipes


class Command(BaseCommand):

    @property
    def help(self):
        return 'Create a game fixture based on a recipe.'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipe',
            type=str,
            help='Identifier of the game recipe to be used.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        recipe_identifier = options['recipe']
        recipe = recipes[recipe_identifier]
        variant = models.Variant.objects.get(
            identifier=recipe.variant_identifier
        )
        recipe(self.stdout.write).bake(variant)
