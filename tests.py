from dependencies import *
from process_move import *

# test_are_equal ----------------------------------------------------------------------------------

def test_are_equal(actual, expected):
    if actual != expected:
        raise Exception("Expected '{}' but got '{}'.".format(expected, actual))

def unit_testing():
    
    # piece exists and belongs to user ------------------------------------------------------------
    
    test_are_equal(
        # true - should return piece
        piece_exists_and_belongs_to_user(
            {"origin": "lon", "nation": "england"}, 
            [{"territory": "lon", "owner": "england"}],
            ), 
        {"territory": "lon", "owner": "england"})
        
    test_are_equal(
        # false - piece is in location but does not belong to order nation
        piece_exists_and_belongs_to_user(
            {"origin": "lon", "nation": "england"}, 
            [{"territory": "lon", "owner": "france"}],
            ), 
        False)
        
    test_are_equal(
        # false - piece belongs to order nation but is not in location
        piece_exists_and_belongs_to_user(
            {"origin": "lon", "nation": "england"}, 
            [{"territory": "nwy", "owner": "england"}],
            ), 
        False)
        
    test_are_equal(
        # false - piece is not in location and does not belong to user
        piece_exists_and_belongs_to_user(
            {"origin": "lon", "nation": "england"}, 
            [{"territory": "nwy", "owner": "france"}],
            ), 
        False)
        
    # territory is neighbour ----------------------------------------------------------------------
        
    test_are_equal(
        territory_is_neighbour(
            "lon", 
            "wal",
            ), 
        True)
    test_are_equal(
        territory_is_neighbour(
            "lon", 
            "eng",
            ), 
        True)
    test_are_equal(
        territory_is_neighbour(
            "lon", 
            "par",
            ), 
        False)
        
        
    test_are_equal(
        territory_is_accessible_by_piece_type(
            origin, 
            territory, 
            piece
        ), 
        True)
        
    print("all units tests successful")
    
unit_testing()