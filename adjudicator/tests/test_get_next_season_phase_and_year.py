import unittest

from adjudicator.base import Phase, Season
from adjudicator.nation import Nation
from adjudicator.piece import Army
from adjudicator.territory import InlandTerritory
from adjudicator.processor import get_next_season_phase_and_year
from .base import AdjudicatorTestCaseMixin


class TestGetNextSeasonPhaseAndYear(AdjudicatorTestCaseMixin, unittest.TestCase):

    def test_spring_order_to_retreat(self):
        army = Army(self.state, 1, 1, 1)
        army.dislodged_decision = 'dislodged'
        result = get_next_season_phase_and_year(self.state)
        self.assertEqual(result, (Season.SPRING, Phase.RETREAT, 1900))

    def test_spring_order_to_fall_order(self):
        result = get_next_season_phase_and_year(self.state)
        self.assertEqual(result, (Season.FALL, Phase.ORDER, 1900))

    def test_fall_order_to_retreat(self):
        self.state.season = Season.FALL
        army = Army(self.state, 1, 1, 1)
        army.dislodged_decision = 'dislodged'
        result = get_next_season_phase_and_year(self.state)
        self.assertEqual(result, (Season.FALL, Phase.RETREAT, 1900))

    def test_fall_order_to_build_surplus(self):
        self.state.season = Season.FALL
        n = Nation(self.state, 1, 'England')
        Army(self.state, 1, n.id, 1)
        result = get_next_season_phase_and_year(self.state)
        self.assertEqual(result, (Season.FALL, Phase.BUILD, 1900))

    def test_fall_order_to_spring_next_year(self):
        self.state.season = Season.FALL
        result = get_next_season_phase_and_year(self.state)
        self.assertEqual(result, (Season.SPRING, Phase.ORDER, 1901))
