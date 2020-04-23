import unittest

from adjudicator.state import data_to_state
from adjudicator import order
from adjudicator.territory import CoastalTerritory, InlandTerritory, \
    SeaTerritory


class TestDataToState(unittest.TestCase):

    def test_sea_territory(self):
        data = {
            'orders': [],
            'pieces': [],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'sea',
                    'name': 'Adriatic Sea',
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': None,
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.territories[0]), SeaTerritory)
        self.assertEqual(state.territories[0].name, 'Adriatic Sea')
        self.assertEqual(state.territories[0].id, 1)

    def test_coastal_territory(self):
        data = {
            'orders': [],
            'pieces': [],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'coastal',
                    'name': 'Brest',
                    'nationality': 1,
                    'controlled_by': 1,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': [2, 3],
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.territories[0]), CoastalTerritory)
        self.assertEqual(state.territories[0].name, 'Brest')
        self.assertEqual(state.territories[0].nationality, 1)
        self.assertEqual(state.territories[0].controlled_by, 1)
        self.assertEqual(state.territories[0].supply_center, True)
        self.assertEqual(state.territories[0].id, 1)

    def test_inland_territory(self):
        data = {
            'orders': [],
            'pieces': [],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'inland',
                    'name': 'Paris',
                    'nationality': 1,
                    'controlled_by': 1,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': None,
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.territories[0]), InlandTerritory)
        self.assertEqual(state.territories[0].name, 'Paris')
        self.assertEqual(state.territories[0].nationality, 1)
        self.assertEqual(state.territories[0].controlled_by, 1)
        self.assertEqual(state.territories[0].supply_center, True)
        self.assertEqual(state.territories[0].id, 1)

    def test_named_coast(self):
        data = {
            'orders': [],
            'pieces': [],
            'named_coasts': [
                {
                    '_id': 1,
                    'name': 'Spain South Coast',
                    'territory_id': 1,
                    'neighbour_ids': [2],
                }
            ],
            'territories': [
                {
                    '_id': 1,
                    'type': 'coastal',
                    'name': 'Spain',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': [2, 3],
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.named_coasts[0].parent), CoastalTerritory)
        self.assertEqual(state.named_coasts[0].name, 'Spain South Coast')
        self.assertEqual(state.named_coasts[0].id, 1)

    def test_piece(self):
        data = {
            'orders': [],
            'pieces': [
                {
                    '_id': 0,
                    'type': 'army',
                    'nation': 1,
                    'territory_id': 1,
                }
            ],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'coastal',
                    'name': 'Spain',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': [2, 3],
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.pieces[0].territory), CoastalTerritory)
        self.assertEqual(state.pieces[0].__class__.__name__, 'Army')
        self.assertEqual(state.pieces[0].nation, 1)

    def test_hold(self):
        data = {
            'orders': [
                {
                    '_id': 1,
                    'type': 'hold',
                    'nation': 1,
                    'source_id': 1,
                    'piece_type': None,
                }
            ],
            'pieces': [],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'coastal',
                    'name': 'Spain',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': [2, 3],
                },
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.orders[0].source), CoastalTerritory)
        self.assertEqual(type(state.orders[0]), order.Hold)
        self.assertEqual(state.orders[0].nation, 1)

    def test_move(self):
        data = {
            'orders': [
                {
                    '_id': 1,
                    'type': 'move',
                    'nation': 1,
                    'source_id': 1,
                    'target_id': 2,
                    'piece_type': None,
                }
            ],
            'pieces': [],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'coastal',
                    'name': 'Spain',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': [2, 3],
                },
                {
                    '_id': 2,
                    'type': 'coastal',
                    'name': 'Portugal',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [1, 3, 4, 5],
                    'shared_coast_ids': [1, 3],
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.orders[0].source), CoastalTerritory)
        self.assertEqual(type(state.orders[0].target), CoastalTerritory)
        self.assertEqual(type(state.orders[0]), order.Move)
        self.assertEqual(state.orders[0].nation, 1)

    def test_support(self):
        data = {
            'orders': [
                {
                    '_id': 1,
                    'type': 'support',
                    'nation': 1,
                    'source_id': 1,
                    'target_id': 2,
                    'aux_id': 2,
                    'piece_type': None,
                }
            ],
            'pieces': [],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'coastal',
                    'name': 'Spain',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': [2, 3],
                },
                {
                    '_id': 2,
                    'type': 'coastal',
                    'name': 'Portugal',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [1, 3, 4, 5],
                    'shared_coast_ids': [1, 3],
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.orders[0].source), CoastalTerritory)
        self.assertEqual(type(state.orders[0].target), CoastalTerritory)
        self.assertEqual(type(state.orders[0].aux), CoastalTerritory)
        self.assertEqual(type(state.orders[0]), order.Support)
        self.assertEqual(state.orders[0].nation, 1)

    def test_convoy(self):
        data = {
            'orders': [
                {
                    '_id': 1,
                    'type': 'convoy',
                    'nation': 1,
                    'source_id': 1,
                    'target_id': 2,
                    'aux_id': 2,
                    'piece_type': None,
                }
            ],
            'pieces': [],
            'named_coasts': [],
            'territories': [
                {
                    '_id': 1,
                    'type': 'coastal',
                    'name': 'Spain',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [2, 3, 4, 5],
                    'shared_coast_ids': [2, 3],
                },
                {
                    '_id': 2,
                    'type': 'coastal',
                    'name': 'Portugal',
                    'nationality': None,
                    'controlled_by': None,
                    'supply_center': True,
                    'neighbour_ids': [1, 3, 4, 5],
                    'shared_coast_ids': [1, 3],
                }
            ]
        }
        state = data_to_state(data)
        self.assertEqual(type(state.orders[0].source), CoastalTerritory)
        self.assertEqual(type(state.orders[0].target), CoastalTerritory)
        self.assertEqual(type(state.orders[0].aux), CoastalTerritory)
        self.assertEqual(type(state.orders[0]), order.Convoy)
        self.assertEqual(state.orders[0].nation, 1)
