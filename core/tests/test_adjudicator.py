from django.test import TestCase

from adjudicator.check import ArmyMovesToAdjacentTerritoryNotConvoy
from core import models
from core.game import process_turn
from core.models.base import GameStatus, OrderType, OutcomeType, PieceType, Phase, Season
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

        self.livonia = models.Territory.objects.get(id='standard-livonia')
        self.norway = models.Territory.objects.get(id='standard-norway')
        self.st_petersburg = models.Territory.objects.get(id='standard-st-petersburg')
        self.st_petersburg_south_coast = models.NamedCoast.objects.get(id='standard-st-petersburg-south-coast')
        self.st_petersburg_north_coast = models.NamedCoast.objects.get(id='standard-st-petersburg-north-coast')

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

    def test_move_st_petersburg_south_coast_to_gulf_of_bothnia(self):
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.FLEET,
            nation=self.russia,
        )
        gulf_of_bothnia = models.Territory.objects.get(id='standard-gulf-of-bothnia')
        models.PieceState.objects.create(
            named_coast=self.st_petersburg_south_coast,
            piece=piece,
            territory=self.st_petersburg,
            turn=self.turn,
        )
        order = models.Order.objects.create(
            nation=self.russia,
            source=self.st_petersburg,
            target=gulf_of_bothnia,
            turn=self.turn,
            type=OrderType.MOVE,
        )
        process_turn(self.turn)
        order.refresh_from_db()
        self.assertFalse(order.illegal)

    def test_st_petersburg_and_norway_shared_coast(self):
        self.assertTrue(self.st_petersburg in self.norway.shared_coasts.all())
        self.assertTrue(self.st_petersburg in self.norway.neighbours.all())
        self.assertTrue(self.norway in self.st_petersburg.shared_coasts.all())
        self.assertTrue(self.norway in self.st_petersburg.neighbours.all())
        self.assertTrue(self.norway in self.st_petersburg_north_coast.neighbours.all())

    def test_move_st_petersburg_north_coast_to_norway(self):
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.FLEET,
            nation=self.russia,
        )
        models.PieceState.objects.create(
            named_coast=self.st_petersburg_north_coast,
            piece=piece,
            territory=self.st_petersburg,
            turn=self.turn,
        )
        order = models.Order.objects.create(
            nation=self.russia,
            source=self.st_petersburg,
            target=self.norway,
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

    def test_build_fleet_st_petersburg_north_coast(self):
        self.turn.season = Season.FALL
        self.turn.phase = Phase.BUILD
        self.turn.save()
        models.TerritoryState.objects.create(
            controlled_by=self.russia,
            territory=self.st_petersburg,
            turn=self.turn,
        )
        order = models.Order.objects.create(
            nation=self.russia,
            source=self.st_petersburg,
            piece_type=PieceType.FLEET,
            target_coast=self.st_petersburg_north_coast,
            turn=self.turn,
            type=OrderType.BUILD,
        )
        new_turn = process_turn(self.turn)
        order.refresh_from_db()
        self.assertFalse(order.illegal)
        new_turn.piecestates.get(
            territory=self.st_petersburg,
            named_coast=self.st_petersburg_north_coast,
            piece__nation=self.russia
        )

    def test_illegal_retreat_removes_piece(self):
        self.turn.phase = Phase.RETREAT
        self.turn.save()
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.russia,
        )
        piece_state = models.PieceState.objects.create(
            piece=piece,
            territory=self.norway,
            turn=self.turn,
            must_retreat=True,
        )
        order = models.Order.objects.create(
            nation=self.russia,
            source=self.norway,
            target=self.livonia,
            turn=self.turn,
            type=OrderType.RETREAT,
        )
        new_turn = process_turn(self.turn)
        order.refresh_from_db()
        piece.refresh_from_db()
        piece_state.refresh_from_db()

        self.assertTrue(order.illegal)
        self.assertTrue(piece_state.destroyed)
        self.assertTrue(piece.turn_destroyed, self.turn)
        self.assertEqual(new_turn.piecestates.count(), 0)

    def test_contested_retreat_removes_piece(self):
        self.turn.phase = Phase.RETREAT
        self.turn.save()
        st_petersburg_state = models.TerritoryState.objects.get(territory=self.st_petersburg)
        st_petersburg_state.contested = True
        st_petersburg_state.save()
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.russia,
        )
        piece_state = models.PieceState.objects.create(
            piece=piece,
            territory=self.norway,
            turn=self.turn,
            must_retreat=True,
        )
        order = models.Order.objects.create(
            nation=self.russia,
            source=self.norway,
            target=self.st_petersburg,
            turn=self.turn,
            type=OrderType.RETREAT,
        )
        new_turn = process_turn(self.turn)
        order.refresh_from_db()
        piece.refresh_from_db()
        piece_state.refresh_from_db()

        self.assertTrue(order.illegal)
        self.assertEqual(order.outcome, OutcomeType.FAILS)
        self.assertTrue(piece_state.destroyed)
        self.assertTrue(piece.turn_destroyed, self.turn)
        self.assertEqual(new_turn.piecestates.count(), 0)

    def test_failed_retreat_removes_piece(self):
        self.turn.phase = Phase.RETREAT
        self.turn.save()
        piece_norway = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.russia,
        )
        piece_state_norway = models.PieceState.objects.create(
            piece=piece_norway,
            territory=self.norway,
            turn=self.turn,
            must_retreat=True,
        )
        piece_livonia = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.russia,
        )
        piece_state_livonia = models.PieceState.objects.create(
            piece=piece_livonia,
            territory=self.livonia,
            turn=self.turn,
            must_retreat=True,
        )
        order_norway = models.Order.objects.create(
            nation=self.russia,
            source=self.norway,
            target=self.st_petersburg,
            turn=self.turn,
            type=OrderType.RETREAT,
        )
        order_livonia = models.Order.objects.create(
            nation=self.russia,
            source=self.livonia,
            target=self.st_petersburg,
            turn=self.turn,
            type=OrderType.RETREAT,
        )
        new_turn = process_turn(self.turn)
        order_norway.refresh_from_db()
        order_livonia.refresh_from_db()
        piece_norway.refresh_from_db()
        piece_livonia.refresh_from_db()
        piece_state_norway.refresh_from_db()
        piece_state_livonia.refresh_from_db()

        self.assertFalse(order_livonia.illegal)
        self.assertFalse(order_norway.illegal)
        self.assertEqual(order_livonia.outcome, OutcomeType.FAILS)
        self.assertEqual(order_norway.outcome, OutcomeType.FAILS)
        self.assertTrue(piece_state_norway.destroyed)
        self.assertTrue(piece_norway.turn_destroyed, self.turn)
        self.assertTrue(piece_state_livonia.destroyed)
        self.assertTrue(piece_livonia.turn_destroyed, self.turn)
        self.assertEqual(new_turn.piecestates.count(), 0)

    def test_no_order_removes_piece(self):
        self.turn.phase = Phase.RETREAT
        self.turn.save()
        st_petersburg_state = models.TerritoryState.objects.get(territory=self.st_petersburg)
        st_petersburg_state.contested = True
        st_petersburg_state.save()
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.russia,
        )
        piece_state = models.PieceState.objects.create(
            piece=piece,
            territory=self.norway,
            turn=self.turn,
            must_retreat=True,
        )
        new_turn = process_turn(self.turn)
        piece.refresh_from_db()
        piece_state.refresh_from_db()

        self.assertTrue(piece_state.destroyed)
        self.assertTrue(piece.turn_destroyed, self.turn)
        self.assertEqual(new_turn.piecestates.count(), 0)

    def test_disband(self):
        self.turn.phase = Phase.BUILD
        self.turn.save()
        piece = models.Piece.objects.create(
            game=self.game,
            type=PieceType.ARMY,
            nation=self.russia,
        )
        piece_state = models.PieceState.objects.create(
            piece=piece,
            territory=self.st_petersburg,
            turn=self.turn,
            must_retreat=True,
        )
        order_st_petersburg = models.Order.objects.create(
            nation=self.russia,
            source=self.st_petersburg,
            turn=self.turn,
            type=OrderType.DISBAND,
        )
        new_turn = process_turn(self.turn)
        order_st_petersburg.refresh_from_db()
        piece.refresh_from_db()
        piece_state.refresh_from_db()

        self.assertEqual(order_st_petersburg.outcome, OutcomeType.SUCCEEDS)
        self.assertTrue(piece.turn_disbanded, self.turn)
        self.assertEqual(new_turn.piecestates.count(), 0)
