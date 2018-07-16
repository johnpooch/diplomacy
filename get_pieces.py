from dependencies import *
# get pieces --------------------------------------------------------------------------------------

def get_pieces():
    return [piece for piece in mongo.db.pieces.find()]