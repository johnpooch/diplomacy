from service.command_processor import Challenge
from service.models import Nation, Order, Piece
from service.tests.base import InitialGameStateTestCase as TestCase
from service.tests.base import HelperMixin, TerritoriesMixin


class TestChallenge(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json']

    def setUp(self):
        super().setUp()
        self.initialise_territories()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )

    def test_challenge(self):
        """

        """
        piece = Piece.objects.get(territory=self.paris)
        c = Challenge(piece, self.paris)
        c.dislodged()
