from django.test import TestCase

from adjudicator.check import ArmyMovesToAdjacentTerritoryNotConvoy
from core import models
from core.game import process_turn
from core.models.base import GameStatus, OrderType, PieceType, Phase, Season
from . import DiplomacyTestCaseMixin


class TestAdjudicator(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = models.Variant.objects.get(id='standard')
        self.game = models.Game.objects.create(
            num_players=7,
            status=GameStatus.ACTIVE,
            variant=self.variant,
        )
        self.turn = models.Turn.objects.create(
            current_turn=True,
            game=self.game,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1900,
        )
        self.england = models.Nation.objects.get(id='standard-england')
        self.russia = models.Nation.objects.get(id='standard-russia')
        self.turkey = models.Nation.objects.get(id='standard-turkey')
        self.patch_process_turn_apply_async()

    def test_move_st_petersburg_south_coast_to_gulf_of_bothnia(self):
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.FLEET,
            nation=self.russia,
        )
        st_petersburg = models.Territory.objects.get(id='standard-st-petersburg')
        st_petersburg_south_coast = models.NamedCoast.objects.get(id='standard-st-petersburg-south-coast')
        gulf_of_bothnia = models.Territory.objects.get(id='standard-gulf-of-bothnia')
        for nation in models.Nation.objects.all():
            models.NationState.objects.create(
                nation=nation,
                turn=self.turn,
            )
        for territory in models.Territory.objects.all():
            models.TerritoryState.objects.create(
                territory=territory,
                turn=self.turn,
            )
        models.PieceState.objects.create(
            named_coast=st_petersburg_south_coast,
            piece=piece,
            territory=st_petersburg,
            turn=self.turn,
        )
        order = models.Order.objects.create(
            nation=self.russia,
            source=st_petersburg,
            target=gulf_of_bothnia,
            turn=self.turn,
            type=OrderType.MOVE,
        )
        process_turn(self.turn)
        order.refresh_from_db()
        self.assertFalse(order.illegal)

    def test_st_petersburg_and_norway_shared_coast(self):
        st_petersburg = models.Territory.objects.get(id='standard-st-petersburg')
        st_petersburg_north_coast = models.NamedCoast.objects.get(id='standard-st-petersburg-north-coast')
        norway = models.Territory.objects.get(id='standard-norway')
        self.assertTrue(st_petersburg in norway.shared_coasts.all())
        self.assertTrue(st_petersburg in norway.neighbours.all())
        self.assertTrue(norway in st_petersburg.shared_coasts.all())
        self.assertTrue(norway in st_petersburg.neighbours.all())
        self.assertTrue(norway in st_petersburg_north_coast.neighbours.all())

    def test_move_st_petersburg_north_coast_to_norway(self):
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.FLEET,
            nation=self.russia,
        )
        st_petersburg = models.Territory.objects.get(id='standard-st-petersburg')
        st_petersburg_north_coast = models.NamedCoast.objects.get(id='standard-st-petersburg-north-coast')
        norway = models.Territory.objects.get(id='standard-norway')
        for nation in models.Nation.objects.all():
            models.NationState.objects.create(
                nation=nation,
                turn=self.turn,
            )
        for territory in models.Territory.objects.all():
            models.TerritoryState.objects.create(
                territory=territory,
                turn=self.turn,
            )
        models.PieceState.objects.create(
            named_coast=st_petersburg_north_coast,
            piece=piece,
            territory=st_petersburg,
            turn=self.turn,
        )
        order = models.Order.objects.create(
            nation=self.russia,
            source=st_petersburg,
            target=norway,
            turn=self.turn,
            type=OrderType.MOVE,
        )
        process_turn(self.turn)
        order.refresh_from_db()
        self.assertFalse(order.illegal)

    def test_move_from_liverpool_to_london(self):
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.england,
        )
        liverpool = models.Territory.objects.get(id='standard-liverpool')
        london = models.Territory.objects.get(id='standard-london')
        for nation in models.Nation.objects.all():
            models.NationState.objects.create(
                nation=nation,
                turn=self.turn,
            )
        for territory in models.Territory.objects.all():
            models.TerritoryState.objects.create(
                territory=territory,
                turn=self.turn,
            )
        models.PieceState.objects.create(
            piece=piece,
            territory=liverpool,
            turn=self.turn,
        )
        order = models.Order.objects.create(
            nation=self.england,
            source=liverpool,
            target=london,
            turn=self.turn,
            type=OrderType.MOVE,
        )
        process_turn(self.turn)
        order.refresh_from_db()
        self.assertTrue(order.illegal)
        self.assertEqual(order.illegal_code, ArmyMovesToAdjacentTerritoryNotConvoy.code)
        self.assertEqual(order.illegal_verbose, ArmyMovesToAdjacentTerritoryNotConvoy.message)

    def test_turkey_does_not_take_bulgaria(self):
        self.turn.season = Season.FALL
        self.turn.save()
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.turkey,
        )
        bulgaria = models.Territory.objects.get(id='standard-bulgaria')
        greece = models.Territory.objects.get(id='standard-greece')
        for nation in models.Nation.objects.all():
            models.NationState.objects.create(
                nation=nation,
                turn=self.turn,
            )
        for territory in models.Territory.objects.all():
            models.TerritoryState.objects.create(
                territory=territory,
                turn=self.turn,
            )
        models.PieceState.objects.create(
            piece=piece,
            territory=bulgaria,
            turn=self.turn,
        )
        order = models.Order.objects.create(
            nation=self.turkey,
            source=bulgaria,
            target=greece,
            turn=self.turn,
            type=OrderType.MOVE,
        )
        new_turn = process_turn(self.turn)
        order.refresh_from_db()
        self.assertFalse(order.illegal)
        old_bulgaria_state = self.turn.territorystates.get(territory=bulgaria)
        new_bulgaria_state = new_turn.territorystates.get(territory=bulgaria)
        self.assertIsNone(old_bulgaria_state.captured_by)
        self.assertIsNone(new_bulgaria_state.controlled_by)
