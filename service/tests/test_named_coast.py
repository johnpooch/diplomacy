from django.test import TestCase


class TestNamedCoast(TestCase):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json']

    def test_one(self):
        pass
