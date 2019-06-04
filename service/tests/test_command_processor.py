from django.test import TestCase

from service.command_processor import CommandProcessor
from service.command import Hold, Move
from service.border import Border, IdentifiedCoastBorder
from service.identified_coast import IdentifiedCoast
from service.piece import Army, Fleet
from service.territory import InlandTerritory, CoastalTerritory, SeaTerritory

    # TODO Special Coasts

class TestBasicMovementFleet(TestCase):

    def setUp(self):
        self.territories = []

        self.paris = InlandTerritory("par")
        self.brest = CoastalTerritory("bre")
        self.gascony = CoastalTerritory("gas")
        self.marseilles = CoastalTerritory("mar")
        self.english_channel = SeaTerritory("eng")
        self.irish_sea = SeaTerritory("iri")
        self.north_atlantic = SeaTerritory("nat")

        self.fleet_ec = Fleet(self.english_channel, "france")
        self.fleet_brest = Fleet(self.brest, "france")
        self.fleet_mar = Fleet(self.marseilles, "france")

        self.borders = [
            Border(self.paris, self.brest),
            Border(self.brest, self.gascony, shared_coast=True),
            Border(self.marseilles, self.gascony),
            Border(self.english_channel, self.brest),
            Border(self.irish_sea, self.english_channel),
            Border(self.north_atlantic, self.irish_sea),
        ]

    def test_sea_to_adjacent_sea_territory(self):
        commands = [Move("france", self.english_channel, self.irish_sea)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.fleet_ec], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_sea_to_adjacent_coastal_territory(self):
        commands = [Move("france", self.english_channel, self.brest)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.fleet_ec], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_coastal_to_adjacent_coastal_territory_if_shared_coast(self):
        commands = [Move("france", self.brest, self.gascony)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.fleet_brest], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_coastal_to_adjacent_coastal_territory_if_not_shared_coast(self):
        commands = [Move("france", self.marseilles, self.gascony)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.fleet_mar], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

    def test_adjacent_inland_territory(self):
        commands = [Move("france", self.brest, self.paris)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.fleet_brest], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

    def test_non_adjacent_sea_territory(self):
        commands = [Move("france", self.english_channel, self.north_atlantic)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.fleet_ec], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

    def test_non_adjacent_coastal_territory(self):
        commands = [Move("france", self.irish_sea, self.brest)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.fleet_brest], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")


class TestBasicMovementArmy(TestCase):

    def setUp(self):
        self.territories = []

        self.paris = InlandTerritory("par")
        self.brest = CoastalTerritory("bre")
        self.burgundy = InlandTerritory("bur")
        self.marseilles = CoastalTerritory("mar")
        self.munich = InlandTerritory("mun")
        self.english_channel = SeaTerritory("eng")

        self.army_par = Army(self.paris, "france")
        self.army_bre = Army(self.brest, "france")

        self.borders = [
            Border(self.paris, self.brest),
            Border(self.paris, self.burgundy),
            Border(self.english_channel, self.brest),
        ]

        pieces = [
            Army(self.paris, "france"),
            Fleet(self.english_channel, "france"),
        ]

    def test_can_hold(self):
        commands = [Hold("france", self.paris)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.army_par], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_hold_when_no_piece_in_source(self):
        commands = [Hold("france", self.paris)]
        processor = CommandProcessor(self.territories, self.borders, [], [], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

    def test_hold_non_friendly_piece(self):
        pieces = [Army(self.paris, "england")]
        commands = [Hold("france", self.paris)]
        processor = CommandProcessor(self.territories, self.borders, [], pieces, commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

    def test_adjacent_inland_territory(self):
        commands = [Move("france", self.paris, self.burgundy)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.army_par], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_adjacent_coastal_territory(self):
        commands = [Move("france", self.paris, self.brest)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.army_par], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_adjacent_sea_territory(self):
        commands = [Move("france", self.brest, self.english_channel)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.army_bre], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

    def test_non_adjacent_inland_territory(self):
        commands = [Move("france", self.paris, self.munich)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.army_par], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

    def test_coastal_to_non_adjacent_coastal_territory_without_convoy(self):
        commands = [Move("france", self.brest, self.marseilles)]
        processor = CommandProcessor(self.territories, self.borders, [], [self.army_bre], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")


class TestIdentifiedCoastMovementFleet(TestCase):

    def setUp(self):
        self.territories = []

        self.spain_sc = IdentifiedCoast("spa-sc")
        self.spain_nc = IdentifiedCoast("spa-nc")

        self.spain = CoastalTerritory("spa", identified_coasts=(self.spain_nc, self.spain_sc))
        self.marseilles = CoastalTerritory("mar")
        self.gascony = CoastalTerritory("gas")
        self.portugal = CoastalTerritory("por")
        self.mid_atlantic = SeaTerritory("mid")
        self.western_med = SeaTerritory("wes")
        self.gulf_of_lyon = SeaTerritory("gol")

        self.fleet_spa_nc = Fleet(self.spain, "france", identified_coast=self.spain_nc)

        self.borders = [
            Border(self.spain, self.marseilles, shared_coast=True),
            Border(self.spain, self.gascony, shared_coast=True),
            Border(self.spain, self.portugal, shared_coast=True),
            Border(self.spain, self.mid_atlantic),
            Border(self.spain, self.western_med),
            Border(self.spain, self.gulf_of_lyon),
        ]

        self.identified_coast_borders = [
            IdentifiedCoastBorder(self.mid_atlantic, self.spain_nc),
            IdentifiedCoastBorder(self.gascony, self.spain_nc),
            IdentifiedCoastBorder(self.portugal, self.spain_nc),
            IdentifiedCoastBorder(self.mid_atlantic, self.spain_sc),
            IdentifiedCoastBorder(self.western_med, self.spain_sc),
            IdentifiedCoastBorder(self.gulf_of_lyon, self.spain_sc),
            IdentifiedCoastBorder(self.marseilles, self.spain_sc),
            IdentifiedCoastBorder(self.portugal, self.spain_sc),
        ]

    def test_coast_to_adjacent_sea(self):
        commands = [Move("france", self.spain, self.mid_atlantic)]
        processor = CommandProcessor(self.territories, self.borders, self.identified_coast_borders, [self.fleet_spa_nc], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_coast_to_adjacent_coast(self):
        commands = [Move("france", self.spain, self.gascony)]
        processor = CommandProcessor(self.territories, self.borders, self.identified_coast_borders, [self.fleet_spa_nc], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "success")

    def test_coast_to_non_adjacent_coast(self):
        commands = [Move("france", self.spain, self.marseilles)]
        processor = CommandProcessor(self.territories, self.borders, self.identified_coast_borders, [self.fleet_spa_nc], commands)
        updated_command = processor.process_commands()[0]
        self.assertEqual(updated_command.result, "invalid")

