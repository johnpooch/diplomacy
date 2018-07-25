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
        
    def __str__(self):
        return "piece at {}, belonging to {}, hold.".format(self.piece.territory, self.player)

class Move(Order):
    def __init__(self, player, piece, target):
        Order.__init__(self, player, piece)
        self.target = target
        
    def __repr__(self):
        return "Move({}, {}, {})".format(self.player, self.piece.territory, self.target)
        
    def __str__(self):
        return "piece at {}, belonging to {}, move to {}.".format(self.piece.territory, self.player, self.target)
        
class Support(Order):
    def __init__(self, player, piece, supported_piece, target):
        Order.__init__(self, player, piece)
        self.target = target
        self.supported_piece = supported_piece
        
    def __repr__(self):
        return "Support({}, {}, {}, {})".format(self.player, self.piece.territory, self.supported_piece.territory, self.target)
        
    def __str__(self):
        return "piece at {}, belonging to {}, support {} into {}.".format(self.piece.territory, self.player, self.supported_piece.territory, self.target)
        
class Convoy(Order):
    def __init__(self, player, piece, convoyed_piece, target):
        Order.__init__(self, player, piece)
        self.target = target
        self.convoyed_piece = convoyed_piece
    
    def __repr__(self):
        return "Convoy({}, {}, {}, {})".format(self.player, self.piece.territory, self.convoyed_piece.territory, self.target)
        
    def __str__(self):
        return "piece at {}, belonging to {}, convoy {} to {}.".format(self.piece.territory, self.player, self.convoyed_piece.territory, self.target)
        
class Retreat(Order):
    def __init__(self, player, piece, target):
        Order.__init__(self, player, piece)
        self.target = target
        
    def __repr__(self):
        return "Retreat({}, {}, {})".format(self.player, self.piece.territory, self.target)
        
    def __str__(self):
        return "piece at {}, belonging to {}, retreat to {}.".format(self.piece.territory, self.player, self.target)
        
class Build(Order):
    def __init__(self, player, piece, target, piece_type):
        Order.__init__(self, player, piece)
        self.target = target
        self.piece_type = piece_type
        
    def __repr__(self):
        return "Build({}, {}, {})".format(self.player, self.piece.territory, self.target)
        
    def __str__(self):
        return "{} build {} at {}.".format(self.player, self.piece_type, self.target)
        
        
order_1 = Hold("england", piece_1)
order_2 = Move("france", piece_2, "mid")
order_3 = Support("france", piece_1, piece_2, "mid")
order_4 = Convoy("england", piece_2, piece_1, "mid")
order_5 = Retreat("england", piece_1, "mid")
order_6 = Build("england", piece_1, "mid", "army")
    