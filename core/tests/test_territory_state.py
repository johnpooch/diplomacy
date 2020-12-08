from django.test import TestCase

from core.models.base import Phase, Season
from core.tests import DiplomacyTestCaseMixin


class TestTerritoryState(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.spring_turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.england = self.variant.nations.create(name='England')
        self.france = self.variant.nations.create(name='France')
        self.fall_turn = self.create_test_turn(
            game=self.game,
            season=Season.FALL,
        )
        self.build_turn = self.create_test_turn(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
        )

    def test_copy_new_turn(self):
        territory_state = self.create_test_territory_state(
            turn=self.spring_turn,
            bounce_occurred=True,
        )
        new_territory_state = territory_state.copy_to_new_turn(self.fall_turn)
        self.assertEqual(new_territory_state.turn, self.fall_turn)

    def test_copy_bounce_occured(self):
        territory_state = self.create_test_territory_state(
            turn=self.spring_turn,
            bounce_occurred=True,
        )
        new_territory_state = territory_state.copy_to_new_turn(self.fall_turn)
        self.assertTrue(new_territory_state.contested)

    def test_copy_contested(self):
        territory_state = self.create_test_territory_state(
            turn=self.spring_turn,
            contested=True,
        )
        new_territory_state = territory_state.copy_to_new_turn(self.fall_turn)
        self.assertFalse(new_territory_state.contested)

    def test_change_possession_no_occupier(self):
        territory_state = self.create_test_territory_state(
            turn=self.fall_turn,
            contested=True,
            controlled_by=self.england,
        )
        new_territory_state = territory_state.copy_to_new_turn(self.build_turn)
        self.assertEqual(new_territory_state.controlled_by, self.england)

    def test_change_possession_occupier_english(self):
        territory_state = self.create_test_territory_state(
            turn=self.fall_turn,
            contested=True,
            controlled_by=self.england,
        )
        piece = self.create_test_piece(game=self.game, nation=self.england)
        self.create_test_piece_state(
            turn=self.fall_turn,
            piece=piece,
            territory=territory_state.territory,
        )
        new_territory_state = territory_state.copy_to_new_turn(self.build_turn)
        self.assertEqual(new_territory_state.controlled_by, self.england)

    def test_change_possession_occupier_french(self):
        territory_state = self.create_test_territory_state(
            turn=self.fall_turn,
            contested=True,
            controlled_by=self.england,
            captured_by=self.france,
        )
        new_territory_state = territory_state.copy_to_new_turn(self.build_turn)
        self.assertEqual(new_territory_state.controlled_by, self.france)
