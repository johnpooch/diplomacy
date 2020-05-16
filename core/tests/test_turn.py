
from django.contrib.auth.models import User
from django.test import TestCase

from core import factories, models
from core.models.base import PieceType, Phase, Season


class TestTurn(TestCase):

    def setUp(self):
        self.variant = factories.StandardVariantFactory()
        self.user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game.participants.add(self.user)
        self.retreat_turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.FALL,
            year=1901,
        )

    def test_ready_to_process_retreat(self):
        england = self.variant.nations.get(name='England')
        france = self.variant.nations.get(name='France')
        other_user = factories.UserFactory()
        self.game.participants.add(other_user)
        england_state = models.NationState.objects.create(
            turn=self.retreat_turn,
            nation=england,
            user=other_user
        )
        france_state = models.NationState.objects.create(
            turn=self.retreat_turn,
            nation=france,
            user=self.user
        )
        piece = models.Piece.objects.create(
            game=self.game,
            nation=france,
            type=PieceType.ARMY,
        )
        models.PieceState.objects.create(
            piece=piece,
            turn=self.retreat_turn,
            must_retreat=True,
        )
        self.assertFalse(self.retreat_turn.ready_to_process)
        # only nation states which have orders to submit must finalize
        france_state.orders_finalized = True
        france_state.save()
        self.assertTrue(self.retreat_turn.ready_to_process)
