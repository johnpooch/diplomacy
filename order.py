from piece import *

class Order():
    def __init__(self, player, piece):
        self.player = player
        self.piece = piece
        self.success = True
        self.report = ""
        
    def fail(self, report_string):
        self.report = report_string
        self.success = False
        
class Hold(Order):
    def __init__(self, player, piece):
        Order.__init__(self, player, piece)
        
    def __repr__(self):
        return "Hold({}, {})".format(self.player, self.piece.territory)

class Move(Order):
    def __init__(self, player, piece, target):
        Order.__init__(self, player, piece)
        self.target = target
        
    def __repr__(self):
        return "Move({}, {}, {})".format(self.player, self.piece.territory, self.target)
        
class Support(Order):
    def __init__(self, player, piece, supported_piece, target):
        Order.__init__(self, player, piece)
        self.target = target
        self.supported_piece = supported_piece
        
    def __repr__(self):
        return "Support({}, {}, {}, {})".format(self.player, self.piece.territory, self.supported_piece.territory, self.target)
        
class Convoy(Order):
    def __init__(self, player, piece, convoyed_piece, target):
        Order.__init__(self, player, piece)
        self.target = target
        self.convoyed_piece = convoyed_piece
    
    def __repr__(self):
        return "Convoy({}, {}, {}, {})".format(self.player, self.piece.territory, self.convoyed_piece.territory, self.target)
        
order_1 = Hold("england", piece_1)
order_2 = Move("france", piece_2, "mid")
order_3 = Support("france", piece_1, piece_2, "mid")
order_4 = Convoy("england", piece_2, piece_1, "mid")

print(repr(order_1))
print(repr(order_2))
print(repr(order_3))
print(repr(order_3))
    