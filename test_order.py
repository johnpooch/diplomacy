import unittest
from order import *
from piece import *
from nation import *
from initial_game_state import *


# DO I NEED TO TEST ORDERING PIECES BELONGING TO ANOTHER COUNTRY?

""" ARMY MOVEMENT: An army can be ordered to move into an adjacent inland or coastal provence. An Army cannot be ordered to move into a water province. """

class Test_Army_Move(unittest.TestCase):
    
    def setUp(self):
        self.test_piece = Army(bre, france)
        self.move_1 = Move(france, bre, par)
        setattr(self.move_1, "piece", self.test_piece)
    
    def test_move_to_inland(self):
        
        setattr(self.move_1, "target", par)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, par)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_to_coastal(self):
        
        setattr(self.move_1, "target", pic)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, pic)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_to_not_adjacent(self):
        
        setattr(self.move_1, "target", bel)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bre)
        self.assertEqual(self.move_1.report, "move failed: bel is not a neighbour of bre and is not accessible by convoy")
        
    def test_move_to_water(self):
        
        setattr(self.move_1, "target", eng)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bre)
        self.assertEqual(self.move_1.report, "move failed: eng is not accessible by army at bre")
        
        
        
""" FLEET MOVEMENT: A fleet can be ordered to move to ana adjacent water province or coastal province. Fleets cannot be ordered to move to an inland province. """

class Test_Fleet_Move(unittest.TestCase):
    
    def setUp(self):
        self.test_piece = Fleet(eng, france)
        self.move_1 = Move(france, eng, mid)
        setattr(self.move_1, "piece", self.test_piece)
    
    def test_move_to_water(self):
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, mid)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_to_coastal(self):
        setattr(self.move_1, "target", lon)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, lon)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_to_not_adjacent(self):
        setattr(self.move_1, "target", hol)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, eng)
        self.assertEqual(self.move_1.report, "move failed: hol is not a neighbour of eng and is not accessible by convoy")
        
""" A fleet in a coastal province can be ordered to move to an adjacent coastal province if it has a shared coastline. """
        
class Test_Fleet_Move_Coastal(unittest.TestCase):
        
    def setUp(self):
        self.test_piece = Fleet(rom, italy)
        self.move_1 = Move(italy, rom, nap)
        setattr(self.move_1, "piece", self.test_piece)
        
    def test_move_to_shared_coast(self):
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, nap)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_to_adjacent_coast_not_shared(self):
        setattr(self.move_1, "target", apu)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, rom)
        self.assertEqual(self.move_1.report, "move failed: apu is not accessible by fleet at rom")
        

""" KIEL AND CONSTANTINOPLE: Fleets can enter Kiel and Constantinople along one coast and be considered anywhere along the coastline. For example, a fleet could move frokm the Black Sea to Constantinople on one turn and then on a later turn move from Constantinople to the Aegean Sea. Likewise a fleet could move from Holland to Kiel on one turn and then move from Kiel to Berlin on a later turn. This does not mean that units can jump over these provinces."""

class Test_Fleet_Move_Con(unittest.TestCase):
        
    def setUp(self):
        self.test_piece = Fleet(bla, turkey)
        self.move_1 = Move(turkey, bla, con)
        setattr(self.move_1, "piece", self.test_piece)
        
    def test_move_from_bla_to_con(self):
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, con)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_bla_to_aeg(self):
        setattr(self.move_1, "target", aeg)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bla)
        self.assertEqual(self.move_1.report, "move failed: aeg is not a neighbour of bla and is not accessible by convoy")

    def test_move_from_con_to_aeg(self):
        self.test_piece = Fleet(con, turkey)
        self.move_1 = Move(turkey, con, aeg)
        setattr(self.move_1, "piece", self.test_piece)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, aeg)
        self.assertEqual(self.move_1.report, "")
        
class Test_Fleet_Move_Kie(unittest.TestCase):

    def test_move_from_hol_to_kie(self):
        self.move_1 = Move(germany, hol, kie)
        setattr(self.move_1, "piece", Fleet(hol, germany))
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, kie)
        self.assertEqual(self.move_1.report, "")

    def test_move_from_kie_to_ber(self):
        self.move_1 = Move(germany, kie, ber)
        setattr(self.move_1, "piece", Fleet(kie, ber))
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, ber)
        self.assertEqual(self.move_1.report, "")
        
""" SWEDEN AND DENMARK: An army or fleet in Sweden can move to Denmark in one turn and vice versa. Baltic Sea cannot move directly into Skaggerak and vice versa."""




if __name__ == '__main__':
    unittest.main()