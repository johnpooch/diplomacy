from django.core.exceptions import ValidationError


from service.command_validator import ArmyMoveValidator, FleetMoveValidator, \
    get_command_validator
from service.models import Challenge, Command, NamedCoast, Nation, Order, Piece
from service.tests.base import HelperMixin, TerritoriesMixin
from .base import InitialGameStateTestCase as TestCase


class TestClean(TestCase, HelperMixin, TerritoriesMixin):
    
    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_raises_validation_error_when_move_invalid(self):
        """
        """
        command = self.move_command(self.paris, self.english_channel)
        with self.assertRaises(ValueError):
            command.save()


class TestCreateChallenge(TestCase, HelperMixin, TerritoriesMixin):

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_army_move_creates_challenge(self):
        """
        The ``process()`` method on a valid army move command will create a
        challenge.
        """
        command = self.move_command(self.paris, self.burgundy)
        challenges = Challenge.objects.all()
        self.assertEqual(Challenge.objects.count(), 0)
        command.process()
        self.assertEqual(Challenge.objects.count(), 1)

        # challenge created with correct piece and target
        challenge = Challenge.objects.get()
        piece = Piece.objects.get(territory=self.paris)
        self.assertEqual(piece, challenge.piece)
        self.assertEqual(self.burgundy, challenge.territory)

    def test_fleet_move_creates_challenge(self):
        """
        The ``process()`` method on a valid fleet move command will create a
        challenge.
        """
        command = self.move_command(self.brest, self.english_channel)
        challenges = Challenge.objects.all()
        self.assertEqual(Challenge.objects.count(), 0)
        command.process()
        self.assertEqual(Challenge.objects.count(), 1)


class TestSupportChallenge(TestCase, HelperMixin, TerritoriesMixin):

    # TODO test support validity

    fixtures = ['nations.json', 'territories.json', 'pieces.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_army_support_challenge(self):
        """
        The ``process()`` method on a valid army support command will add a
        support to a challenge.
        """
        pass
