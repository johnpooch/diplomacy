from django.core.exceptions import ValidationError

from service.command_validator import ArmyMoveValidator, FleetMoveValidator, \
    get_command_validator
from service.command_processor import Challenge, CommandProcessor
from service.models import Move, NamedCoast, Nation, Order, Piece
from service.tests.base import HelperMixin, TerritoriesMixin
from .base import InitialGameStateTestCase as TestCase


class TestCommandProcessor(TestCase, TerritoriesMixin, HelperMixin):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json', 'supply_centers.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_challenge_created_for_every_hold_command(self):
        """
        A ``Challenge`` instance is created and added to
        ``CommandProcessor.challenges`` for every hold command in the db.
        """
        command = self.hold(self.brest)
        command.save()
        cp = CommandProcessor()
        self.assertEqual(len(cp.challenges), 1)

    def test_challenge_created_for_every_move_command(self):
        """
        A ``Challenge`` instance is created and added to
        ``CommandProcessor.challenges`` for every move command in the db.
        """
        command = self.move(self.brest, self.english_channel)
        command.save()
        cp = CommandProcessor()
        self.assertEqual(len(cp.challenges), 1)

    def test_challenge_created_for_every_support_command(self):
        """
        A ``Challenge`` instance is created and added to
        ``CommandProcessor.challenges`` for every support command. The
        ``Challenge.territory`` is the source territory of the support command.
        """
        command = self.support(self.brest, self.picardy, self.paris)
        command.save()
        cp = CommandProcessor()
        self.assertEqual(len(cp.challenges), 1)

    def test_challenge_created_for_every_convoy_command(self):
        """
        A ``Challenge`` instance is created and added to
        ``CommandProcessor.challenges`` for every convoy command. The
        ``Challenge.territory`` is the source territory of the convoy command.
        """
        Piece.objects.create(
            territory=self.gulf_of_lyon,
            type=Piece.PieceType.FLEET,
            nation=Nation.objects.get(name='France')
        )
        command = self.convoy(self.gulf_of_lyon, self.spain, self.marseilles)
        command.save()
        cp = CommandProcessor()
        self.assertEqual(len(cp.challenges), 1)

    def test_support_added_to_challenge_when_support(self):
        """
        A piece which supports another piece into a territory is added to
        ``Challenge.supporting_pieces``.
        """
        Piece.objects.create(
            territory=self.mid_atlantic,
            type=Piece.PieceType.FLEET,
            nation=Nation.objects.get(name='France')
        )
        move = self.move(self.brest, self.english_channel)
        move.save()
        support = self.support(self.mid_atlantic, self.english_channel,
                               self.brest)
        support.save()
        cp = CommandProcessor()
        challenge = cp._get_challenge(move.piece, move.target_territory)
        self.assertEqual(len(challenge.supporting_pieces), 1)
        self.assertEqual(challenge.supporting_pieces[0], support.piece)

    def test_convoy_added_to_challenge_when_convoy(self):
        """
        A piece which convoys another piece into a territory is added to
        ``Challenge.convoying_pieces``.
        """
        Piece.objects.create(
            territory=self.gulf_of_lyon,
            type=Piece.PieceType.FLEET,
            nation=Nation.objects.get(name='France')
        )
        move = self.move(self.marseilles, self.spain)
        move.save()
        convoy = self.convoy(self.gulf_of_lyon, self.spain,
                             self.marseilles)
        convoy.save()
        cp = CommandProcessor()
        challenge = cp._get_challenge(move.piece, move.target_territory)
        self.assertEqual(len(challenge.convoying_pieces), 1)
        self.assertEqual(challenge.convoying_pieces[0], convoy.piece)

class TestDislodged(self):

    fixtures = ['nations.json', 'territories.json', 'named_coasts.json',
                'pieces.json', 'supply_centers.json']

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            nation=Nation.objects.get(name='France'),
            turn=self.turn,
        )
        self.initialise_territories()

    def test_dislodged(self):
        """
        A piece with support attacking another piece without support causes the
        piece without support to be dislodged.
        """
        Piece.objects.create(
            territory=self.english_channel,
            type=Piece.PieceType.FLEET,
            nation=Nation.objects.get(name='France')
        )
        Piece.objects.create(
            territory=self.irish_sea,
            type=Piece.PieceType.FLEET,
            nation=Nation.objects.get(name='France')
        )
        Piece.objects.create(
            territory=self.mid_atlantic,
            type=Piece.PieceType.FLEET,
            nation=Nation.objects.get(name='England')
        )
        move = self.move(self.marseilles, self.spain)
        move.save()
        cp = CommandProcessor()
        challenge = cp._get_challenge(move.piece, move.target_territory)
        self.assertEqual(len(challenge.convoying_pieces), 1)
        self.assertEqual(challenge.convoying_pieces[0], convoy.piece)
