from django.core.management.base import BaseCommand
from django.db import transaction

from core import models
from fixtures.recipe import recipes as recipe_conf


class Command(BaseCommand):

    @property
    def help(self):
        return 'Create game fixtures.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipe',
            type=str,
            help=(
                'Identifier of the game recipe to be used. If empty all '
                'recipes will be created'
            )
        )

    @transaction.atomic
    def handle(self, *args, **options):
        recipe_identifier = options.get('recipe')
        if recipe_identifier:
            recipes = recipe_conf[recipe_identifier]
        else:
            recipes = recipe_conf.values()
        for recipe in recipes:
            variant = models.Variant.objects.get(
                id=recipe.variant_id
            )
            recipe(self.stdout.write).bake(variant)
