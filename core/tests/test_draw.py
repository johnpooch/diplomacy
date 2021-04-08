from unittest.mock import patch

from django.test import TestCase

from core import models
from core.models.base import DrawStatus, DrawResponse, GameStatus
from core.tests import DiplomacyTestCaseMixin

set_status_path = 'core.models.Draw.set_status'
anonymous_path = 'core.models.Draw._responses_unanimous'
has_enough_responses_path = 'core.models.Draw._has_enough_responses'


class TestDraw(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.england = self.create_test_nation(
            variant=self.variant,
            name='England'
        )
        self.france = self.create_test_nation(
            variant=self.variant,
            name='France'
        )
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
        )

    def create_draw_response(self, nation, response):
        return models.DrawResponse.objects.create(
            draw=self.draw,
            nation=nation,
            response=response,
            user=self.user,
        )

    def test_str(self):
        self.draw.nations.add(self.france)
        self.assertEqual(
            str(self.draw),
            'England - [France] - Proposed',
        )

    @patch(set_status_path)
    def test_unanimous_accepted(self, _):
        self.create_draw_response(self.france, DrawResponse.ACCEPTED)
        self.create_draw_response(self.england, DrawResponse.ACCEPTED)
        self.assertTrue(self.draw._responses_unanimous())

    @patch(set_status_path)
    def test_unanimous_rejected(self, _):
        self.create_draw_response(self.france, DrawResponse.REJECTED)
        self.create_draw_response(self.england, DrawResponse.REJECTED)
        self.assertTrue(self.draw._responses_unanimous())

    @patch(set_status_path)
    def test_not_unanimous(self, _):
        self.create_draw_response(self.france, DrawResponse.ACCEPTED)
        self.create_draw_response(self.england, DrawResponse.REJECTED)
        self.assertFalse(self.draw._responses_unanimous())

    @patch(set_status_path)
    def test_enough_responses(self, _):
        self.create_test_nation_state(
            nation=self.france,
            turn=self.turn,
            user=self.user,
        )
        self.create_draw_response(
            nation=self.france,
            response=DrawResponse.ACCEPTED,
        )
        self.assertTrue(self.draw._has_enough_responses())

    @patch(set_status_path)
    def test_not_enough_responses(self, _):
        self.create_test_nation_state(
            nation=self.france,
            turn=self.turn,
            user=self.user,
        )
        self.create_test_nation_state(
            nation=self.england,
            turn=self.turn,
            user=self.user,
        )
        self.create_draw_response(
            nation=self.france,
            response=DrawResponse.ACCEPTED,
        )
        self.assertFalse(self.draw._has_enough_responses())

    def test_set_status_not_proposed(self):
        self.draw.status = DrawStatus.EXPIRED
        self.draw.save()
        with self.assertRaises(ValueError):
            self.draw.set_status()

    @patch(anonymous_path)
    @patch(has_enough_responses_path)
    def test_set_status_unanimous_but_not_enough_responses(
        self, anonymous, enough_responses
    ):
        anonymous.return_value = False
        enough_responses.return_value = True
        status = self.draw.set_status()
        self.draw.refresh_from_db()
        self.assertEqual(self.draw.status, DrawStatus.PROPOSED)
        self.assertEqual(status, DrawStatus.PROPOSED)

    @patch(anonymous_path)
    @patch(has_enough_responses_path)
    def test_set_status_enough_responses_but_not_unanimous(
        self, anonymous, enough_responses
    ):
        anonymous.return_value = True
        enough_responses.return_value = False
        status = self.draw.set_status()
        self.draw.refresh_from_db()
        self.assertEqual(self.draw.status, DrawStatus.PROPOSED)
        self.assertEqual(status, DrawStatus.PROPOSED)

    @patch(anonymous_path)
    @patch(has_enough_responses_path)
    def test_set_status_accepted(
        self, anonymous, enough_responses
    ):
        anonymous.return_value = True
        enough_responses.return_value = True
        self.create_draw_response(self.england, DrawResponse.ACCEPTED)
        self.draw.status = DrawStatus.PROPOSED
        self.draw.save()
        status = self.draw.set_status()
        self.draw.refresh_from_db()
        self.assertEqual(self.draw.status, DrawStatus.ACCEPTED)
        self.assertEqual(status, DrawStatus.ACCEPTED)

    @patch(anonymous_path)
    @patch(has_enough_responses_path)
    def test_set_status_rejected(
        self, anonymous, enough_responses
    ):
        anonymous.return_value = True
        enough_responses.return_value = True
        self.create_draw_response(self.england, DrawResponse.REJECTED)
        self.draw.status = DrawStatus.PROPOSED
        self.draw.save()
        status = self.draw.set_status()
        self.draw.refresh_from_db()
        self.assertEqual(self.draw.status, DrawStatus.REJECTED)
        self.assertEqual(status, DrawStatus.REJECTED)
