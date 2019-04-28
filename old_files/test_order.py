import unittest
from process_orders import process_orders
from order import *
from piece import *
from nation import *
from initial_game_state import *

""" ARMY MOVEMENT: An army can be ordered to move into an adjacent inland or coastal provence. An Army cannot be ordered to move into a water province. """

class Test_Army_Move(unittest.TestCase):
    
    game_properties = Game_Properties(1901, Spring_Order_Phase)
    
    def setUp(self):
        self.test_piece = Army("", bre, france)
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
        
        
        
""" FLEET MOVEMENT: A fleet can be ordered to move to an adjacent water province or coastal province. Fleets cannot be ordered to move to an inland province. """

class Test_Fleet_Move(unittest.TestCase):
    
    def setUp(self):
        self.test_piece = Fleet("", eng, france)
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
        
    def test_move_to_inland(self):
        self.test_piece = Fleet("", gas, france)
        self.move_1 = Move(france, gas, spa)
        setattr(self.move_1, "piece", self.test_piece)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, gas)
        self.assertEqual(self.move_1.report, "move failed: spa is not accessible by fleet at gas")
        
    def test_move_to_not_adjacent(self):
        setattr(self.move_1, "target", hol)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, eng)
        self.assertEqual(self.move_1.report, "move failed: hol is not a neighbour of eng and is not accessible by convoy")
        
""" A fleet in a coastal province can be ordered to move to an adjacent coastal province if it has a shared coastline. """
        
class Test_Fleet_Move_Coastal(unittest.TestCase):
        
    def setUp(self):
        self.test_piece = Fleet("", rom, italy)
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
        self.test_piece = Fleet("", bla, turkey)
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
        self.test_piece = Fleet("", con, turkey)
        self.move_1 = Move(turkey, con, aeg)
        setattr(self.move_1, "piece", self.test_piece)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, aeg)
        self.assertEqual(self.move_1.report, "")
        
class Test_Fleet_Move_Kie(unittest.TestCase):

    def test_move_from_hol_to_kie(self):
        self.move_1 = Move(germany, hol, kie)
        setattr(self.move_1, "piece", Fleet("", hol, germany))
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, kie)
        self.assertEqual(self.move_1.report, "")

    def test_move_from_kie_to_ber(self):
        self.move_1 = Move(germany, kie, ber)
        setattr(self.move_1, "piece", Fleet("", kie, ber))
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, ber)
        self.assertEqual(self.move_1.report, "")
        
""" SWEDEN AND DENMARK: An army or fleet in Sweden can move to Denmark in one turn and vice versa. Baltic Sea cannot move directly into Skaggerak and vice versa."""

class Test_Fleet_Move_Swe(unittest.TestCase):

    def test_move_from_den_to_swe(self):
        self.move_1 = Move(germany, den, swe)
        setattr(self.move_1, "piece", Fleet("", den, germany))
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, swe)
        self.assertEqual(self.move_1.report, "")

    def test_move_from_bal_to_ska(self):
        self.move_1 = Move(germany, bal, ska)
        setattr(self.move_1, "piece", Fleet("", bal, germany))
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bal)
        self.assertEqual(self.move_1.report, "move failed: ska is not a neighbour of bal and is not accessible by convoy")

""" BLUGARIA, SPAIN, STP: A fleet entering one of these territories can move to a coast that is adjacent to that coast only. A fleet at Spain's North Coast cannot be ordered to the Western Mediterranean of the Gulf of Lyon or to Marseilles. """

class Test_Fleet_Move_Spa_Nc(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", spa_nc, france)
        self.move_1 = Move(france, spa_nc, mar)
        setattr(self.move_1, "piece", self.test_piece)

    def test_move_from_spa_nc_to_mar(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, spa_nc)
        self.assertEqual(self.move_1.report, "move failed: mar is not a neighbour of spa_nc and is not accessible by convoy")
        
    def test_move_from_spa_nc_to_wes(self):
        setattr(self.move_1, "target", wes)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, spa_nc)
        self.assertEqual(self.move_1.report, "move failed: wes is not a neighbour of spa_nc and is not accessible by convoy")
        
    def test_move_from_spa_nc_to_gol(self):
        setattr(self.move_1, "target", gol)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, spa_nc)
        self.assertEqual(self.move_1.report, "move failed: gol is not a neighbour of spa_nc and is not accessible by convoy")
        
    def test_move_from_spa_nc_to_por(self):
        setattr(self.move_1, "target", por)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, por)
        self.assertEqual(self.move_1.report, "")
        
class Test_Fleet_Move_Spa_Sc(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", spa_sc, france)
        self.move_1 = Move(france, spa_sc, mar)
        setattr(self.move_1, "piece", self.test_piece)

    def test_move_from_spa_sc_to_mar(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, mar)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_spa_sc_to_wes(self):
        setattr(self.move_1, "target", wes)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, wes)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_spa_sc_to_gol(self):
        setattr(self.move_1, "target", gas)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, spa_sc)
        self.assertEqual(self.move_1.report, "move failed: gas is not a neighbour of spa_sc and is not accessible by convoy")
        
    def test_move_from_spa_sc_to_spa(self):
        setattr(self.move_1, "target", spa)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, spa_sc)
        self.assertEqual(self.move_1.report, "move failed: spa is not a neighbour of spa_sc and is not accessible by convoy")
        
class Test_Fleet_Move_Mid_To_Spa_Sc(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", mid, france)
        self.move_1 = Move(france, mid, spa_sc)
        setattr(self.move_1, "piece", self.test_piece)
        
    def test_move_from_mid_to_spa_sc(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, spa_sc)
        self.assertEqual(self.move_1.report, "")
        
class Test_Fleet_Move_Mid_To_Spa_Nc(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", mid, france)
        self.move_1 = Move(france, mid, spa_nc)
        setattr(self.move_1, "piece", self.test_piece)
        
    def test_move_from_mid_to_spa_sc(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, spa_nc)
        self.assertEqual(self.move_1.report, "")
        
class Test_Fleet_Move_Bul_Sc(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", bul_sc, france)
        self.move_1 = Move(france, bul_sc, con)
        setattr(self.move_1, "piece", self.test_piece)

    def test_move_from_bul_sc_to_con(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, con)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_bul_sc_to_aeg(self):
        setattr(self.move_1, "target", aeg)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, aeg)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_bul_sc_to_gre(self):
        setattr(self.move_1, "target", gre)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, gre)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_bul_sc_to_bla(self):
        setattr(self.move_1, "target", bla)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bul_sc)
        self.assertEqual(self.move_1.report, "move failed: bla is not a neighbour of bul_sc and is not accessible by convoy")
        
    def test_move_from_bul_sc_to_rum(self):
        setattr(self.move_1, "target", rum)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bul_sc)
        self.assertEqual(self.move_1.report, "move failed: rum is not a neighbour of bul_sc and is not accessible by convoy")
        
class Test_Fleet_Move_bul_ec(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", bul_ec, france)
        self.move_1 = Move(france, bul_ec, con)
        setattr(self.move_1, "piece", self.test_piece)

    def test_move_from_bul_ec_to_con(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, con)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_bul_ec_to_aeg(self):
        setattr(self.move_1, "target", aeg)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bul_ec)
        self.assertEqual(self.move_1.report, "move failed: aeg is not a neighbour of bul_ec and is not accessible by convoy")
        
    def test_move_from_bul_ec_to_gre(self):
        setattr(self.move_1, "target", gre)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bul_ec)
        self.assertEqual(self.move_1.report, "move failed: gre is not a neighbour of bul_ec and is not accessible by convoy")
        
    def test_move_from_bul_ec_to_bla(self):
        setattr(self.move_1, "target", bla)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, bla)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_bul_ec_to_rum(self):
        setattr(self.move_1, "target", rum)
        self.move_1.process_order()
        
        self.assertEqual(self.move_1.piece.challenging, rum)
        self.assertEqual(self.move_1.report, "")
        
class Test_Fleet_Move_stp_sc(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", stp_sc, france)
        self.move_1 = Move(france, stp_sc, lvn)
        setattr(self.move_1, "piece", self.test_piece)

    def test_move_from_stp_sc_to_lvn(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, lvn)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_stp_sc_to_fin(self):
        setattr(self.move_1, "target", fin)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, fin)
        self.assertEqual(self.move_1.report, "")
            
    def test_move_from_stp_sc_to_bot(self):
        setattr(self.move_1, "target", bot)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, bot)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_stp_sc_to_bar(self):
        setattr(self.move_1, "target", bar)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, stp_sc)
        self.assertEqual(self.move_1.report, "move failed: bar is not a neighbour of stp_sc and is not accessible by convoy")
        
    def test_move_from_stp_sc_to_nwy(self):
        setattr(self.move_1, "target", nwy)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, stp_sc)
        self.assertEqual(self.move_1.report, "move failed: nwy is not a neighbour of stp_sc and is not accessible by convoy")
        
    def test_move_from_stp_sc_to_stp_nc(self):
        setattr(self.move_1, "target", stp_nc)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, stp_sc)
        self.assertEqual(self.move_1.report, "move failed: stp_nc is not a neighbour of stp_sc and is not accessible by convoy")

class Test_Fleet_Move_stp_nc(unittest.TestCase):

    def setUp(self):
        self.test_piece = Fleet("", stp_nc, france)
        self.move_1 = Move(france, stp_nc, lvn)
        setattr(self.move_1, "piece", self.test_piece)

    def test_move_from_stp_nc_to_lvn(self):
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, stp_nc)
        self.assertEqual(self.move_1.report, "move failed: lvn is not a neighbour of stp_nc and is not accessible by convoy")
        
    def test_move_from_stp_nc_to_fin(self):
        setattr(self.move_1, "target", fin)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, stp_nc)
        self.assertEqual(self.move_1.report, "move failed: fin is not a neighbour of stp_nc and is not accessible by convoy")
            
    def test_move_from_stp_nc_to_bot(self):
        setattr(self.move_1, "target", bot)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, stp_nc)
        self.assertEqual(self.move_1.report, "move failed: bot is not a neighbour of stp_nc and is not accessible by convoy")
        
    def test_move_from_stp_nc_to_bar(self):
        setattr(self.move_1, "target", bar)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, bar)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_stp_nc_to_nwy(self):
        setattr(self.move_1, "target", nwy)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, nwy)
        self.assertEqual(self.move_1.report, "")
        
    def test_move_from_stp_nc_to_stp_sc(self):
        setattr(self.move_1, "target", stp_sc)
        self.move_1.process_order()
        self.assertEqual(self.move_1.piece.challenging, stp_nc)
        self.assertEqual(self.move_1.report, "move failed: stp_sc is not a neighbour of stp_nc and is not accessible by convoy")
        

""" SUPPORT: The province to which a unit is providing support must be one to which the supporting unit could have legally moved during that turn. """

class Test_Support_1(unittest.TestCase):

    def test_army_par_support_bur_pic(self):
        
        self.test_piece_1 = Army("", par, france)
        self.test_piece_2 = Army("", bur, france)
        
        self.order_1 = Support(france, par, bur, pic)
        self.order_2 = Move(france, bur, pic)
        
        setattr(self.order_1, "piece", self.test_piece_1)
        setattr(self.order_2, "piece", self.test_piece_2)
        
        self.order_1.process_order()
        self.order_2.process_order()
        
        self.assertEqual(self.order_2.piece.strength, {pic: 1})
        self.assertEqual(self.order_1.report, "") 

    # have to use separate territories because of this issue: https://github.com/HypothesisWorks/hypothesis/issues/59

    def test_army_vie_support_bud_ser(self):
        
        self.test_piece_1 = Army("", vie, france)
        self.test_piece_2 = Army("", bud, france)
        
        self.order_1 = Support(france, vie, bud, ser)
        self.order_2 = Move(france, bud, ser)
        
        setattr(self.order_1, "piece", self.test_piece_1)
        setattr(self.order_2, "piece", self.test_piece_2)
        
        self.order_1.process_order()
        self.order_2.process_order()
        
        self.assertEqual(self.order_2.piece.strength, {})
        self.assertEqual(self.order_1.report, "support failed: army at vie cannot support bud to ser")
        

    def test_fleet_bre_support_lon_eng(self):
        self.test_piece_1 = Fleet("", bre, france)
        self.test_piece_2 = Fleet("", lon, france)
        
        self.order_1 = Support(france, bre, lon, eng)
        self.order_2 = Move(france, lon, eng)
        
        setattr(self.order_1, "piece", self.test_piece_1)
        setattr(self.order_2, "piece", self.test_piece_2)
        
        self.order_1.process_order()
        self.order_2.process_order()
        
        self.assertEqual(self.order_2.piece.strength, {eng: 1})
        self.assertEqual(self.order_1.report, "")
        print()

if __name__ == '__main__':
    unittest.main()