from django.test import TestCase

from service.tests.utils import TerritoriesMixin


class TestTerritory(TestCase, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        self.initialise_territories()

    def test_is_complex(self):
        self.assertTrue(self.spain.is_complex())

    def test_is_not_complex(self):
        self.assertFalse(self.brest.is_complex())

    def test_is_inland(self):
        self.assertTrue(self.paris.is_inland())

    def test_is_not_inland(self):
        self.assertFalse(self.brest.is_inland())
