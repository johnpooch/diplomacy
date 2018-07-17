from dependencies import *
from get_pieces import get_pieces
from get_orders import get_orders

# does piece have most support --------------------------------------------------------------------

#  REFACTOR
def piece_has_most_support(piece, pieces_to_compare):
    
    if not piece["challenging"] in piece["support"]:
        piece["support"][piece["challenging"]] = 0
    for other_piece in pieces_to_compare:
        if not piece["challenging"] in other_piece["support"]:
            other_piece["support"][piece["challenging"]] = 0
    return all(piece["support"][piece["challenging"]] > other_piece["support"][piece["challenging"]] for other_piece in pieces_to_compare)
    
    
    
def find_other_pieces_challenging_territory(piece):
    territory = piece["challenging"]
    return [other_piece for other_piece in get_pieces() if other_piece["challenging"] == territory and piece["territory"] != other_piece["territory"]]
    
# resolve challenges ------------------------------------------------------------------------------

def resolve_challenges():
    write_to_log("\n")
    for piece in get_pieces():
        pieces_to_compare = find_other_pieces_challenging_territory(piece)
        
        if piece_has_most_support(piece, pieces_to_compare) or not pieces_to_compare:
            
            previous_territory = piece["territory"]
            new_territory = piece["challenging"]
            mongo.db.pieces.update_one({
                "previous_territory": previous_territory,
                "territory": piece["territory"],
                "owner": piece["owner"]
            }, 
            {
                "$set": {"territory": piece["challenging"]}
            })
            if pieces_to_compare:
                for piece in pieces_to_compare:
                    mongo.db.pieces.update_one({
                        "territory": piece["territory"],
                        "owner": piece["owner"]
                    }, 
                    {
                        "$set": {"must_retreat": True}
                    })
                    write_to_log("{} must retreat".format(piece["territory"]))
        else:
            write_to_log("{}: order failed".format(piece["territory"]))
    return True