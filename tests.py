from dependencies import *
from process_convoy import *
from process_move import *
from process_retreats import *

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
        
    # territory is accessible by piece type -------------------------------------------------------
    
    test_are_equal(
        territory_is_accessible_by_piece_type(
            {"territory": "par", "piece_type": "a"},
            "bur"
            ), 
        True)
    test_are_equal(
        # false - army trying to move to water territory
        territory_is_accessible_by_piece_type(
            {"territory": "bre", "piece_type": "a"},
            "eng"
            ), 
        False)
    test_are_equal(
        # false - army trying to move to water territory
        territory_is_accessible_by_piece_type(
            {"territory": "bre", "piece_type": "a"},
            "eng"
            ), 
        False)
    test_are_equal(
        # false - fleet trying to move to inland territory
        territory_is_accessible_by_piece_type(
            {"territory": "bre", "piece_type": "f"},
            "par"
            ), 
        False)
        
    # territory shares coast with origin ----------------------------------------------------------
    
    test_are_equal(
        territory_shares_coast_with_origin(
            "kie",
            "hol"
            ), 
        True)
    test_are_equal(
        # false - fleet to move to territory that is not connected by shared coast.
        territory_shares_coast_with_origin(
            "ank",
            "smy"
            ), 
        False)

    # check for neighbour convoy ------------------------------------------------------------------
        
    test_are_equal(
        target_accessible_by_convoy(
            {"origin": "lon", "target": "nwy", "nation": "england"},
            {"territory": "lon", "convoyed_by": ["nth"]},
            "lon"), 
        True)
    test_are_equal(
        # true - piece has two convoying pieces between it and target.
        target_accessible_by_convoy(
            {"origin": "lon", "target": "swe", "nation": "england"},
            {"territory": "lon", "convoyed_by": ["nth", "ska"]},
            "lon"), 
        True)
        
    test_are_equal(
        # false - piece does not have convoying piece.
        target_accessible_by_convoy(
            {"origin": "lon", "target": "nwy", "nation": "england"},
            {"territory": "lon", "convoyed_by": []},
            "lon"), 
        False)
        
    # object_piece_exists -----------------------------------------------------------------------
        
    test_are_equal(
        object_piece_exists(
            {"object": "lon", "target": "nwy", "nation": "england"},
            [{"territory": "lon"}],
            ),
        True)
    test_are_equal(
        object_piece_exists(
            {"object": "lon", "target": "nwy", "nation": "england"},
            [{"territory": "wal"}],
            ),
        False)
        
    print("all units tests successful")
    
    # piece_is_on_water ---------------------------------------------------------------------------
        
    test_are_equal(
        piece_is_on_water(
            {"territory": "nth"},
            ),
        True)
    test_are_equal(
        piece_is_on_water(
            {"territory": "lon"},
            ),
        False)
    test_are_equal(
        piece_is_on_water(
            {"territory": "par"},
            ),
        False)
        
    # target is not attacker origin ---------------------------------------------------------------
    
    test_are_equal(
        target_is_not_attacker_origin(
            {"territory": "wal", "nation": "england"},
            [
                {"territory": "wal", "nation": "france", "previous_territory": "lon"}, 
                {"territory": "wal","previous_territory": "wal", "nation": "england"}
            ],
            "lon"
            ),
    False)
    
    test_are_equal(
        target_is_not_attacker_origin(
            {"territory": "wal", "nation": "england"},
            [
                {"territory": "wal", "nation": "france", "previous_territory": "yor"}, 
                {"territory": "wal","previous_territory": "wal", "nation": "england"}
            ],
            "lon"
            ),
    True)
    
    
unit_testing()