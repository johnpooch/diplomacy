import unittest
from process_orders import end_turn
from piece import *
from initial_game_state import *

expected_positions = [
    nwy,
    lon,
    nth,
    wal,
    mid,
    por,
    den,
    swe,
    hol,
    rum,
    gre,
    bud,
    tun,
    ion,
    ven,
    ukr,
    bot,
    bul,
    con,
    sev,
    lvp,
    eng,
    pic,
    tyn,
    sil,
    war,
    gal,
    adr,
    eas,
    bla,
    ]

def test_run():
    end_turn("game_histories/game_1/01_spring_1901.txt")
    end_turn("game_histories/game_1/02_fall_1901.txt")
    end_turn("game_histories/game_1/03_fall_build_1901.txt")
    end_turn("game_histories/game_1/04_spring_1902.txt")
    end_turn("game_histories/game_1/05_spring_retreat_1902.txt")
    end_turn("game_histories/game_1/06_fall_1902.txt")
        


class Test_Army_Move(unittest.TestCase):

    def setUp(self):
        test_run()
        self.piece_positions = [piece.territory for piece in Piece.all_pieces]
        
    def tearDown(self):
        pass

    def test_order_history(self):
        self.assertEqual(expected_positions, self.piece_positions)
        
if __name__ == '__main__':
    unittest.main()