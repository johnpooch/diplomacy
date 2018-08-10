from write_to_log import write_to_log
from piece import *

# Phase ===========================================================================================

class Phase():
    def __init__(self):
        pass
    
# Fall Build Phase ------------------------------------------------------------------------------   

class Fall_Build_Phase(Phase):
    def __init__(self):
        self.name = "fall_build_phase"
    
    def end_phase(self):
        return Spring_Order_Phase()

# Retreat Phase -----------------------------------------------------------------------------------

class Retreat_Phase(Phase):
    def __init__(self):
        pass
    
# Fall Retreat Phase ------------------------------------------------------------------------------
    
class Fall_Retreat_Phase(Retreat_Phase):
    def __init__(self):
        self.name = "fall_retreat_phase"
    
    def end_phase(self):
        return Fall_Build_Phase()
    
# Spring Retreat Phase ----------------------------------------------------------------------------
    
class Spring_Retreat_Phase(Retreat_Phase):
    def __init__(self):
        self.name = "spring_retreat_phase"
    
    def end_phase(self):
        return Fall_Order_Phase()
    
# Order Phase -------------------------------------------------------------------------------------
    
class Order_Phase(Phase):
    def __init__(self):
        pass
    
# Fall Order Phase --------------------------------------------------------------------------------
    
class Fall_Order_Phase(Order_Phase):
    def __init__(self):
        self.name = "fall_order_phase"
    
    def end_phase(self):
                
        if any([piece.retreat for piece in Piece.all_pieces]):
            return Fall_Retreat_Phase()
        else:
            return Fall_Build_Phase()
    
# Spring Order Phase ------------------------------------------------------------------------------
    
class Spring_Order_Phase(Order_Phase):
    def __init__(self):
        self.name = "spring_order_phase"
    
    def end_phase(self):
        if any([piece.retreat for piece in Piece.all_pieces]):
            return Spring_Retreat_Phase()
        else:
            return Fall_Order_Phase()