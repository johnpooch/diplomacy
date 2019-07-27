# from django.test import TestCase
from .base import InitialGameStateTestCase as TestCase

from service.models import Challenge, Command, Game, Nation, Order, Phase, \
    Piece, Territory, Turn


class TestValidMove(TestCase):

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.fleet = Piece.objects.get(territory__name='brest')

    def set_fleet_position(self, territory):
        self.fleet.territory = territory
        self.fleet.save()

    def test_sea_to_adjacent_sea_territory(self):
        """
        Fleet can move to adjacent sea territory.
        """
        # Break into method
        self.fleet.territory = Territory.objects.get(name='english channel')
        self.fleet.territory.save()

        target_territory = Territory.objects.get(name='english channel')

        command = Command.objects.create(
            source_territory=self.fleet.territory,
            target_territory=target_territory,
            order=self.order,
            type='M',
        )
        command.check_valid()
        self.assertTrue(command.valid)
        c = Challenge.objects.get()
        self.assertEqual(c.territory, target_territory)

    # def test_sea_to_adjacent_coastal_territory(self):
    #     """
    #     Fleet can move from sea territory to adjacent coastal territory.
    #     """
    #     self.set_fleet_position(self.english_channel)
    #     command = Command.objects.create(
    #         source_territory=self.english_channel,
    #         target_territory=self.brest,
    #         order=self.order,
    #         type='M',
    #     )
    #     command.process()
    #     self.assertTrue(command.success)
    #     self.assertEqual(
    #         command.source_territory.piece.challenging,
    #         self.brest
    #     )

    # def test_coastal_to_adjacent_coastal_territory_if_shared_coast(self):
    #     """
    #     Fleet can move from coastal territory to adjacent coastal territory.
    #     """
    #     self.set_fleet_position(self.brest)
    #     command = Command.objects.create(
    #         source_territory=self.brest,
    #         target_territory=self.gascony,
    #         order=self.order,
    #         type='M',
    #     )
    #     command.process()
    #     self.assertTrue(command.success)
    #     self.assertEqual(
    #         command.source_territory.piece.challenging,
    #         self.gascony
    #     )

    # def test_coastal_to_adjacent_coastal_territory_if_not_shared_coast(self):
    #     """
    #     Fleet cannot move from coastal territory to adjacent coastal territory
    #     when no shared coastline.
    #     """
    #     self.set_fleet_position(self.marseilles)
    #     command = Command.objects.create(
    #         source_territory=self.marseilles,
    #         target_territory=self.gascony,
    #         order=self.order,
    #         type='M',
    #     )
    #     command.process()
    #     self.assertFalse(command.success)
    #     self.assertEqual(command.source_territory.piece.challenging, None)

    # def test_coastal_to_adjacent_inland_territory(self):
    #     """
    #     Fleet cannot move from coastal territory to adjacent inland territory.
    #     """
    #     self.set_fleet_position(self.marseilles)
    #     command = Command.objects.create(
    #         source_territory=self.marseilles,
    #         target_territory=self.paris,
    #         order=self.order,
    #         type='M',
    #     )
    #     command.process()
    #     self.assertFalse(command.success)
    #     self.assertEqual(command.source_territory.piece.challenging, None)

